# SF Express Location Data

This directory contains HTML files with SF Express location data scraped from their official website.

## Files

- **SF Locker.html** - SF Express smart locker locations (319 locations)
- **SF Store.html** - SF Express store locations (86 locations)
- **SF Business Station.html** - SF Express business station locations (21 locations)

## Total Locations

426 real SF Express locations across Hong Kong and Macau

## Data Structure

### SF Locker
- Location Type: LOCKER
- Fields: District, Code, Full Address, Opening Hours (Weekday/Weekend)
- Special: Includes Cold Chain lockers

### SF Store
- Location Type: SHOP
- Fields: District, Code, Address, Business Hours
- Special: Includes airport and Macau locations

### SF Business Station
- Location Type: SHOP
- Fields: District, Address with embedded code, Business Hours
- Special: Business-focused locations

## Loading Data

To load this data into the database:

```bash
# Local development
uv run python manage.py load_sfexpress_data

# Docker
docker-compose exec web uv run python manage.py load_sfexpress_data
```

The data is automatically loaded on first Docker container startup.

## Data Updates

To update the location data:

1. Download latest HTML files from SF Express website
2. Replace files in this directory
3. Run the load command to refresh database

## Source

Data sourced from SF Express Hong Kong official website:
- https://htm.sf-express.com/hk/en/dynamic_function/S.F.Network/
