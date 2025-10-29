# SF Express Locations API

A Django web application for accessing SF Express locker and shop locations with a user-friendly dashboard, API key management, and credit system.

## Features

- **Web Dashboard**: User-friendly interface for registration, login, and account management
- **API Key Management**: Create and manage API keys through the dashboard
- **Credit System**: Track API usage with credits (100 free credits for new users)
- **Locations API**: Query SF Express locker and shop locations via REST API
- **SQLite Database**: Lightweight database for easy setup
- **Admin Panel**: Django admin interface for managing data

## Requirements

- Python 3.10+
- uv (for dependency management)

OR

- Docker and Docker Compose (for containerized deployment)

## Installation

### Option 1: Local Development

1. Install dependencies using uv:
```bash
uv sync
```

2. Run migrations to set up the database:
```bash
uv run python manage.py migrate
```

3. Load sample location data:
```bash
uv run python manage.py load_sample_data
```

4. (Optional) Create a superuser for admin access:
```bash
uv run python manage.py createsuperuser
```

5. Run the development server:
```bash
uv run python manage.py runserver
```

Or use the quick start script:
```bash
./start.sh
```

The application will be available at `http://localhost:8000/`

### Option 2: Docker Deployment (Recommended for Production)

1. Create environment file (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. Build and start the container:
```bash
docker-compose up -d
```

The application will be available at `http://localhost:8000/`

**Docker Features:**
- Automatic database migrations on startup
- Sample data loaded on first run
- Persistent data stored in `./data` directory (mounted to `/data` in container)
- Health checks included
- Automatic restart on failure

**Docker Commands:**

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Create a superuser
docker-compose exec web uv run python manage.py createsuperuser

# Access Django shell
docker-compose exec web uv run python manage.py shell

# Run migrations manually
docker-compose exec web uv run python manage.py migrate
```

**Production Configuration:**

For production deployment, set these environment variables in `.env`:

```env
SECRET_KEY=your-secure-random-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

The application will be available at `http://localhost:8000/`

## Getting Started

### Web Dashboard

1. **Visit the home page**: Open `http://localhost:8000/` in your browser

2. **Register an account**: Click "Register" and create an account
   - You'll receive 100 free credits to get started

3. **Login**: Use your credentials to log in

4. **Access your dashboard**: View your credits, create API keys, and monitor usage
   - Create API keys with descriptive names
   - Copy your API key for use in API requests
   - View transaction history
   - Delete API keys you no longer need

5. **Use the API**: Use your API key to make requests to the locations endpoint

### Endpoints

#### Dashboard Pages (Web Interface)

- `GET /` - Home page with features and pricing
- `GET /register` - User registration page
- `GET /login` - User login page
- `GET /dashboard` - User dashboard (requires login)
- `POST /dashboard/api-keys/create` - Create new API key (requires login)
- `POST /dashboard/api-keys/<id>/delete` - Delete API key (requires login)
- `GET /logout` - Logout

#### API Endpoint (Requires API Key)

- `GET /api/locations` - Get SF Express locations (costs 5 credits per request)
  - Query Parameters:
    - `type` - Filter by "LOCKER" or "SHOP"
    - `district` - Filter by district name (e.g., "Central")
    - `search` - Search by location name

## Using the Locations API

Once you have an API key from the dashboard, use it to query locations:

### Example Request

```bash
curl -X GET "http://localhost:8000/api/locations?type=LOCKER" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Example Response

```json
{
  "count": 5,
  "locations": [
    {
      "id": 1,
      "location_type": "LOCKER",
      "name": "Central Station Smart Locker",
      "address": "MTR Central Station, Exit A",
      "district": "Central and Western",
      "latitude": "22.281610",
      "longitude": "114.158220",
      "phone": "+852-2730-0273",
      "opening_hours": "24/7"
    }
  ],
  "credits_used": 5,
  "credits_remaining": 95
}
```

### Filter Examples

```bash
# Get all lockers
curl -X GET "http://localhost:8000/api/locations?type=LOCKER" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Get all shops
curl -X GET "http://localhost:8000/api/locations?type=SHOP" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Filter by district
curl -X GET "http://localhost:8000/api/locations?district=Central" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Search by name
curl -X GET "http://localhost:8000/api/locations?search=Causeway" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Combine filters
curl -X GET "http://localhost:8000/api/locations?type=LOCKER&district=Wan%20Chai" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000/api"
API_KEY = "your-api-key-here"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Get all locations
response = requests.get(f"{BASE_URL}/locations", headers=headers)
data = response.json()

print(f"Found {data['count']} locations")
print(f"Credits remaining: {data['credits_remaining']}")

for location in data['locations']:
    print(f"- {location['name']} ({location['location_type']})")
```

## Pricing

- **Starter (Free)**: 100 credits for new users
- **Basic**: $10/month - 1,000 credits
- **Pro**: $50/month - 10,000 credits
- **Enterprise**: Custom pricing - Unlimited credits

**API Costs:**
- Location query: 5 credits per request

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/` to:
- Manage users and API keys
- Add/edit SF Express locations
- Adjust user credit balances
- View transaction history

## Location Data

The project includes **426 real SF Express locations** from Hong Kong and Macau:
- 319 Smart Lockers (including Cold Chain lockers)
- 107 Shops and Business Stations

Location data is sourced from SF Express official HTML files in the `docs/` directory.

Load location data with:
```bash
# Local development
uv run python manage.py load_sfexpress_data

# Docker (automatically loaded on first run)
docker-compose exec web uv run python manage.py load_sfexpress_data
```

### Data Features
- Real addresses and districts
- Accurate opening hours
- Phone numbers for each location
- Differentiated locker types (standard and cold chain)
- Hong Kong and Macau coverage

## Project Structure

```
sfexpress-api/
├── manage.py
├── pyproject.toml
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── docker-entrypoint.sh    # Container startup script
├── .dockerignore          # Docker build exclusions
├── .env.example           # Environment variables template
├── data/                  # Persistent data directory (SQLite DB)
│   └── db.sqlite3         # Database file (created on first run)
├── docs/                  # SF Express location data (HTML files)
│   ├── SF Locker.html     # Locker locations
│   ├── SF Store.html      # Store locations
│   └── SF Business Station.html  # Business station locations
├── sfexpress_api/          # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── api/                    # Main application
    ├── models.py           # User, APIKey, CreditBalance, Location
    ├── views.py            # Dashboard and API views
    ├── urls.py             # URL routing
    ├── middleware.py       # API key authentication
    ├── admin.py            # Admin interface
    ├── templates/          # HTML templates
    │   └── api/
    │       ├── base.html
    │       ├── home.html
    │       ├── login.html
    │       ├── register.html
    │       └── dashboard.html
    └── management/
        └── commands/
            ├── load_sample_data.py      # Dummy data (deprecated)
            └── load_sfexpress_data.py   # Real SF Express data
```

## Deployment

### Data Persistence

All persistent data (database, user uploads) is stored in the `/data` directory:
- **Local development**: `./data/` in project root
- **Docker deployment**: Mounted as volume from `./data/` to `/data` in container

The database file is located at `/data/db.sqlite3` and persists across container restarts.

### Environment Variables

Configure the application using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `django-insecure-...` | Django secret key (change in production!) |
| `DEBUG` | `True` | Debug mode (set to `False` in production) |
| `ALLOWED_HOSTS` | `*` | Comma-separated list of allowed hosts |
| `DATA_DIR` | `./data` | Path to persistent data directory |

### Backup

To backup your data:

```bash
# Local development
cp -r data/ backup/

# Docker deployment
docker-compose exec web tar czf /data/backup.tar.gz /data/db.sqlite3
docker cp sfexpress-api:/data/backup.tar.gz ./backup.tar.gz
```

### Reverse Proxy (Production)

For production deployment, use a reverse proxy (nginx, Caddy, Traefik) with SSL:

Example nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Notes

- Change `SECRET_KEY` in production
- Set `DEBUG = False` in production
- Update `ALLOWED_HOSTS` for production deployment
- Use environment variables for sensitive configuration
- Implement rate limiting for production use
- Use HTTPS in production

## Development

### Adding New Locations

Use the Django admin panel or Django shell:

```bash
uv run python manage.py shell
```

```python
from api.models import Location

Location.objects.create(
    location_type='LOCKER',
    name='New Location',
    address='123 Street',
    district='District Name',
    latitude=22.281610,
    longitude=114.158220,
    phone='+852-1234-5678',
    opening_hours='24/7',
    is_active=True
)
```

## License

MIT License
