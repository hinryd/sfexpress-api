from django.core.management.base import BaseCommand
from api.models import Location


class Command(BaseCommand):
    help = 'Load sample SF Express locations into the database'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample locations...')

        locations = [
            # Lockers
            {
                'location_type': 'LOCKER',
                'name': 'Central Station Smart Locker',
                'address': 'MTR Central Station, Exit A',
                'district': 'Central and Western',
                'latitude': 22.281610,
                'longitude': 114.158220,
                'phone': '+852-2730-0273',
                'opening_hours': '24/7',
                'is_active': True
            },
            {
                'location_type': 'LOCKER',
                'name': 'Causeway Bay Smart Locker',
                'address': 'Times Square, Ground Floor',
                'district': 'Wan Chai',
                'latitude': 22.278010,
                'longitude': 114.182710,
                'phone': '+852-2730-0273',
                'opening_hours': '24/7',
                'is_active': True
            },
            {
                'location_type': 'LOCKER',
                'name': 'Tsim Sha Tsui Smart Locker',
                'address': 'Harbour City, Ocean Terminal',
                'district': 'Yau Tsim Mong',
                'latitude': 22.294610,
                'longitude': 114.168810,
                'phone': '+852-2730-0273',
                'opening_hours': '24/7',
                'is_active': True
            },
            {
                'location_type': 'LOCKER',
                'name': 'Mong Kok Smart Locker',
                'address': 'Langham Place, Ground Floor',
                'district': 'Yau Tsim Mong',
                'latitude': 22.318610,
                'longitude': 114.169110,
                'phone': '+852-2730-0273',
                'opening_hours': '24/7',
                'is_active': True
            },
            {
                'location_type': 'LOCKER',
                'name': 'Admiralty Smart Locker',
                'address': 'Pacific Place, Ground Floor',
                'district': 'Central and Western',
                'latitude': 22.277910,
                'longitude': 114.165210,
                'phone': '+852-2730-0273',
                'opening_hours': '24/7',
                'is_active': True
            },

            # Shops
            {
                'location_type': 'SHOP',
                'name': 'SF Express Central Shop',
                'address': '123 Queen\'s Road Central',
                'district': 'Central and Western',
                'latitude': 22.282410,
                'longitude': 114.155310,
                'phone': '+852-2730-1234',
                'opening_hours': 'Mon-Fri: 9:00-19:00, Sat: 9:00-17:00',
                'is_active': True
            },
            {
                'location_type': 'SHOP',
                'name': 'SF Express Causeway Bay Shop',
                'address': '456 Hennessy Road',
                'district': 'Wan Chai',
                'latitude': 22.280110,
                'longitude': 114.183310,
                'phone': '+852-2730-2345',
                'opening_hours': 'Mon-Fri: 9:00-19:00, Sat: 9:00-17:00',
                'is_active': True
            },
            {
                'location_type': 'SHOP',
                'name': 'SF Express Tsim Sha Tsui Shop',
                'address': '789 Nathan Road',
                'district': 'Yau Tsim Mong',
                'latitude': 22.297810,
                'longitude': 114.172110,
                'phone': '+852-2730-3456',
                'opening_hours': 'Mon-Fri: 9:00-19:00, Sat: 9:00-17:00',
                'is_active': True
            },
            {
                'location_type': 'SHOP',
                'name': 'SF Express Mong Kok Shop',
                'address': '321 Argyle Street',
                'district': 'Yau Tsim Mong',
                'latitude': 22.322010,
                'longitude': 114.170510,
                'phone': '+852-2730-4567',
                'opening_hours': 'Mon-Fri: 9:00-19:00, Sat: 9:00-17:00',
                'is_active': True
            },
            {
                'location_type': 'SHOP',
                'name': 'SF Express Wan Chai Shop',
                'address': '654 Lockhart Road',
                'district': 'Wan Chai',
                'latitude': 22.276910,
                'longitude': 114.172410,
                'phone': '+852-2730-5678',
                'opening_hours': 'Mon-Fri: 9:00-19:00, Sat: 9:00-17:00',
                'is_active': True
            },
        ]

        created_count = 0
        for location_data in locations:
            location, created = Location.objects.get_or_create(
                name=location_data['name'],
                defaults=location_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {location.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Already exists: {location.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully loaded {created_count} new locations!')
        )
