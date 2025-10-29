from django.core.management.base import BaseCommand
from api.models import Location
from html.parser import HTMLParser
import re
import os


class TableExtractor(HTMLParser):
    """Extract table data from HTML"""
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_row = []
        self.rows = []
        self.cell_data = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag == 'td' and self.in_row:
            self.in_cell = True
            self.cell_data = ''

    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'tr':
            if self.current_row:
                self.rows.append(self.current_row)
            self.in_row = False
        elif tag == 'td':
            self.in_cell = False
            self.current_row.append(self.cell_data.strip())

    def handle_data(self, data):
        if self.in_cell:
            self.cell_data += data


class Command(BaseCommand):
    help = 'Load SF Express locations from HTML files in docs/ directory'

    def handle(self, *args, **options):
        self.stdout.write('Loading SF Express location data from HTML files...\n')

        docs_dir = 'docs'
        if not os.path.exists(docs_dir):
            self.stdout.write(self.style.ERROR(f'Error: {docs_dir}/ directory not found'))
            return

        # Clear existing locations
        Location.objects.all().delete()
        self.stdout.write('Cleared existing location data')

        total_created = 0

        # Load lockers
        locker_file = os.path.join(docs_dir, 'SF Locker.html')
        if os.path.exists(locker_file):
            count = self.load_lockers(locker_file)
            total_created += count
            self.stdout.write(self.style.SUCCESS(f'Loaded {count} locker locations'))

        # Load stores
        store_file = os.path.join(docs_dir, 'SF Store.html')
        if os.path.exists(store_file):
            count = self.load_stores(store_file)
            total_created += count
            self.stdout.write(self.style.SUCCESS(f'Loaded {count} store locations'))

        # Load business stations
        business_file = os.path.join(docs_dir, 'SF Business Station.html')
        if os.path.exists(business_file):
            count = self.load_business_stations(business_file)
            total_created += count
            self.stdout.write(self.style.SUCCESS(f'Loaded {count} business station locations'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully loaded {total_created} total locations!'))

    def extract_code_from_text(self, text):
        """Extract code like ^852M^ from text"""
        match = re.search(r'\^([A-Z0-9]+)\^', text)
        return match.group(1) if match else None

    def clean_text(self, text):
        """Remove code markers and clean text"""
        text = re.sub(r'\^[A-Z0-9]+\^', '', text)
        return text.strip()

    def parse_hours(self, hours_text):
        """Parse opening hours text"""
        if not hours_text:
            return ''
        hours_text = hours_text.strip()
        if hours_text.lower() in ['24hours', '24 hours']:
            return '24/7'
        if hours_text.lower() == 'closed':
            return 'Closed'
        return hours_text

    def extract_district_from_address(self, address):
        """Extract district name from address string"""
        # Common Hong Kong districts and areas
        districts = [
            # New Territories
            'Tai Wai', 'Sha Tin', 'Ma On Shan', 'Fo Tan', 'Tai Po', 'Fanling',
            'Sheung Shui', 'Tuen Mun', 'Tin Shui Wai', 'Yuen Long', 'Tsing Lung Tau',
            'Ma Wan', 'Sham Tseng', 'Tsuen Wan', 'Tai Wo Hau', 'Kwai Fong',
            'Kwai Chung', 'Tsing Yi', 'Tung Chung', 'Pui O', 'Chek Lap Kok',
            'Mui Wo', 'Discovery Bay', 'Cheung Chau', 'Tiu Keng Leng',
            'Tseung Kwan O', 'Sai Kung',
            # Kowloon
            'Kowloon City', 'Shek Kip Mei', 'Kai Tak', 'Kowloon Tong', 'To Kwa Wan',
            'Whampoa', 'Hung Hom', 'Ho Man Tin', 'Prince Edward', 'Tai Kok Tsui',
            'Mong Kok', 'Yau Ma Tei', 'Jordan', 'Tsim Sha Tsui', 'Sham Shui Po',
            'Cheung Sha Wan', 'Lai Chi Kok', 'Mei Foo',
            # Hong Kong Island
            'Central', 'Admiralty', 'Wan Chai', 'Causeway Bay', 'Tin Hau',
            'Fortress Hill', 'North Point', 'Quarry Bay', 'Tai Koo', 'Sai Wan Ho',
            'Shau Kei Wan', 'Chai Wan', 'Sheung Wan', 'Sai Ying Pun', 'Kennedy Town',
            'Aberdeen', 'Wong Chuk Hang', 'Stanley', 'Repulse Bay', 'Heng Fa Chuen',
            'Shek O'
        ]

        # Sort by length (longest first) to match "Cheung Sha Wan" before "Wan"
        districts.sort(key=len, reverse=True)

        for district in districts:
            if district in address:
                return district

        return 'Unknown'

    def load_lockers(self, file_path):
        """Load SF Locker locations"""
        parser = TableExtractor()
        with open(file_path, 'r', encoding='utf-8') as f:
            parser.feed(f.read())

        created_count = 0
        header_indices = []
        last_district = None  # Track last seen district for Type 2 rows

        # Find headers with "District" and "Locker Full Address"
        for i, row in enumerate(parser.rows):
            if len(row) >= 3 and 'District' in ''.join(row) and 'Address' in ''.join(row):
                header_indices.append(i)

        for header_idx in header_indices:
            # Process rows after this header
            for j in range(header_idx + 1, len(parser.rows)):
                row = parser.rows[j]

                # Stop if we hit another header
                if 'District' in ''.join(row) and 'Address' in ''.join(row):
                    break

                if len(row) < 3:
                    continue

                # Skip navigation/menu rows
                if any(skip in ''.join(row).lower() for skip in ['express', 'delivery', 'service', 'about']):
                    continue

                # Detect row type by checking if first column contains a code (H852...)
                first_col = self.clean_text(row[0])
                is_code_first = bool(re.match(r'H852[A-Z0-9]+', first_col))

                if is_code_first:
                    # Type 2: Code | Address | Hours | Hours | Applicable
                    # No district name - code is in first column
                    if len(row) < 4:
                        continue
                    code = first_col
                    address = self.clean_text(row[1]) if len(row) > 1 else ''
                    hours_weekday = self.parse_hours(row[2]) if len(row) > 2 else ''
                    hours_weekend = self.parse_hours(row[3]) if len(row) > 3 else ''

                    # Try to use last seen district, or extract from address
                    district = last_district if last_district else self.extract_district_from_address(address)
                    if not district or district == 'Unknown':
                        district = self.extract_district_from_address(address)
                else:
                    # Type 1: District | Code | Address | Hours | Hours
                    # Has district name in first column
                    if len(row) < 5:
                        continue
                    district = first_col
                    code = self.clean_text(row[1]) if len(row) > 1 else ''
                    address = self.clean_text(row[2]) if len(row) > 2 else ''
                    hours_weekday = self.parse_hours(row[3]) if len(row) > 3 else ''
                    hours_weekend = self.parse_hours(row[4]) if len(row) > 4 else ''

                    # Remember this district for subsequent Type 2 rows
                    last_district = district

                if not district or len(district) > 100:
                    continue

                if not address or len(address) < 10:
                    continue

                # Extract code from address if not in separate column
                if not code:
                    code = self.extract_code_from_text(address)
                    address = self.clean_text(address)

                # Combine hours
                if hours_weekday == hours_weekend:
                    opening_hours = hours_weekday
                else:
                    opening_hours = f"Mon-Sat: {hours_weekday}, Sun/Holidays: {hours_weekend}"

                # Determine if it's a cold chain locker
                is_cold_chain = 'Cold Chain' in address
                name_suffix = ' (Cold Chain)' if is_cold_chain else ''

                # Create a better name using code if available
                if code:
                    location_name = f"SF Locker {code} - {district}{name_suffix}"
                else:
                    location_name = f"SF Locker - {district}{name_suffix}"

                try:
                    Location.objects.create(
                        location_type='LOCKER',
                        name=location_name,
                        address=address,
                        district=district,
                        phone='+852-2730-0273',
                        opening_hours=opening_hours,
                        is_active=True
                    )
                    created_count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Skipped locker: {str(e)[:100]}'))

        return created_count

    def load_stores(self, file_path):
        """Load SF Store locations"""
        parser = TableExtractor()
        with open(file_path, 'r', encoding='utf-8') as f:
            parser.feed(f.read())

        created_count = 0

        # Look for rows with store data
        for i, row in enumerate(parser.rows):
            if len(row) < 3:
                continue

            # Skip headers and navigation
            if 'District' in row[0] or 'Code' in row[0]:
                continue
            if any(skip in ''.join(row).lower() for skip in ['express', 'delivery', 'about', 'service']):
                continue

            district = self.clean_text(row[0])
            if not district or len(district) > 100:
                continue

            # Check if this looks like a valid location row
            code = self.extract_code_from_text(row[1]) if len(row) > 1 else None

            # Try to find address column
            address = ''
            for col_idx in range(1, min(len(row), 4)):
                if len(row[col_idx]) > 20 and ('Building' in row[col_idx] or 'Floor' in row[col_idx] or 'G/F' in row[col_idx]):
                    address = self.clean_text(row[col_idx])
                    break

            if not address or len(address) < 15:
                continue

            # Get hours from last columns
            hours = ''
            if len(row) >= 3:
                last_cols = [self.parse_hours(row[i]) for i in range(-2, 0) if i + len(row) >= 0]
                last_cols = [h for h in last_cols if h and len(h) < 50]
                if len(last_cols) == 2 and last_cols[0] == last_cols[1]:
                    hours = last_cols[0]
                elif len(last_cols) == 2:
                    hours = f"Mon-Sat: {last_cols[0]}, Sun/Holidays: {last_cols[1]}"
                elif len(last_cols) == 1:
                    hours = last_cols[0]

            try:
                # Check if it's airport or Macau location
                is_airport = 'Airport' in address
                is_macau = 'Macau' in address or district == 'Macau'
                phone = '+853-2873-7373' if is_macau else '+852-2730-0273'

                Location.objects.create(
                    location_type='SHOP',
                    name=f"SF Store - {district}",
                    address=address,
                    district=district,
                    phone=phone,
                    opening_hours=hours or '09:00-20:00',
                    is_active=True
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Skipped store: {str(e)[:100]}'))

        return created_count

    def load_business_stations(self, file_path):
        """Load SF Business Station locations"""
        parser = TableExtractor()
        with open(file_path, 'r', encoding='utf-8') as f:
            parser.feed(f.read())

        created_count = 0

        for row in parser.rows:
            if len(row) < 2:
                continue

            # Skip headers and navigation
            if 'District' in row[0] or any(skip in ''.join(row).lower() for skip in ['express', 'delivery', 'about']):
                continue

            # Format: District | Address with code | Hours
            district = self.clean_text(row[0])
            if not district or len(district) > 100:
                continue

            # Second column should have address with embedded code
            address_col = row[1] if len(row) > 1 else ''
            if not address_col or len(address_col) < 15:
                continue

            code = self.extract_code_from_text(address_col)
            address = self.clean_text(address_col)

            # Third column is usually hours
            hours = ''
            if len(row) >= 3:
                hours_cols = [self.parse_hours(row[i]) for i in range(2, min(len(row), 5))]
                hours_cols = [h for h in hours_cols if h and len(h) < 50 and h.lower() not in ['applicable', '/']]
                if len(hours_cols) >= 2 and hours_cols[0] == hours_cols[1]:
                    hours = hours_cols[0]
                elif len(hours_cols) >= 2:
                    hours = f"Mon-Sat: {hours_cols[0]}, Sun/Holidays: {hours_cols[1]}"
                elif len(hours_cols) == 1:
                    hours = hours_cols[0]

            # Check for Macau locations
            is_macau = 'Macau' in address or district == 'Macau' or 'Macau' in district
            phone = '+853-2873-7373' if is_macau else '+852-2730-0273'

            try:
                Location.objects.create(
                    location_type='SHOP',
                    name=f"SF Business Station - {district}",
                    address=address,
                    district=district,
                    phone=phone,
                    opening_hours=hours or '09:00-20:00',
                    is_active=True
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Skipped business station: {str(e)[:100]}'))

        return created_count
