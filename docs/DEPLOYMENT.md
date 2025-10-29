# SF Express API - Deployment Guide

Complete guide for deploying the SF Express Locations API using Docker.

## Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd sfexpress-api

# Configure environment (optional)
cp .env.example .env
# Edit .env with your settings

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

The application will be available at `http://localhost:8000`

## Architecture

### Container Stack
- **Base Image**: `ghcr.io/astral-sh/uv:debian-slim`
- **Application**: Django web server (port 8000)
- **Database**: SQLite (persistent volume)
- **Data Storage**: `/data` directory (mounted as volume)

### Data Persistence

All persistent data is stored in the `/data` directory:
```
./data/
├── db.sqlite3          # SQLite database
└── .initialized        # First-run marker file
```

This directory is mounted as a Docker volume, ensuring data persists across container restarts.

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```env
# Required for production
SECRET_KEY=your-secure-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Optional
DATA_DIR=/data
```

### Generate a Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or use Docker:
```bash
docker-compose exec web uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Deployment Steps

### 1. Prepare the Server

Install Docker and Docker Compose:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin
```

### 2. Clone and Configure

```bash
# Clone repository
git clone <your-repo-url>
cd sfexpress-api

# Create environment file
cp .env.example .env

# Edit configuration
nano .env
```

Update `.env` with production values:
```env
SECRET_KEY=<generated-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 3. Build and Deploy

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 4. Create Admin User

```bash
docker-compose exec web uv run python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 5. Verify Deployment

```bash
# Check health
curl http://localhost:8000/

# Check API
curl http://localhost:8000/api/locations
```

## Production Setup

### Reverse Proxy with Nginx

1. Install Nginx:
```bash
sudo apt-get install nginx
```

2. Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/sfexpress-api
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/sfexpress-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is set up automatically
sudo certbot renew --dry-run
```

## Maintenance

### View Logs

```bash
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f web
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Check health
docker-compose ps
```

### Database Backup

```bash
# Create backup
docker-compose exec web tar czf /data/backup-$(date +%Y%m%d-%H%M%S).tar.gz /data/db.sqlite3

# Copy to host
docker cp sfexpress-api:/data/backup-*.tar.gz ./backups/

# Or use local copy
cp -r data/ backups/backup-$(date +%Y%m%d-%H%M%S)/
```

### Database Restore

```bash
# Stop application
docker-compose down

# Restore data directory
cp -r backups/backup-YYYYMMDD-HHMMSS/* data/

# Start application
docker-compose up -d
```

### Run Management Commands

```bash
# Create superuser
docker-compose exec web uv run python manage.py createsuperuser

# Django shell
docker-compose exec web uv run python manage.py shell

# Run migrations
docker-compose exec web uv run python manage.py migrate

# Load sample data
docker-compose exec web uv run python manage.py load_sample_data

# Check configuration
docker-compose exec web uv run python manage.py check
```

## Monitoring

### Health Checks

Docker Compose includes automatic health checks:
```bash
# Check health status
docker-compose ps

# View health check logs
docker inspect sfexpress-api --format='{{json .State.Health}}'
```

### Resource Usage

```bash
# Container stats
docker stats sfexpress-api

# Disk usage
du -sh data/
```

## Scaling

### Increase Resources

Update `docker-compose.yml`:
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Check configuration
docker-compose config

# Rebuild
docker-compose up -d --build --force-recreate
```

### Database Issues

```bash
# Reset database (WARNING: deletes all data)
docker-compose down
rm -rf data/db.sqlite3 data/.initialized
docker-compose up -d
```

### Permission Issues

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/
chmod 755 data/
```

## Security Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up HTTPS with SSL certificate
- [ ] Configure firewall (only ports 80, 443, 22)
- [ ] Set up regular backups
- [ ] Enable automatic security updates
- [ ] Monitor logs for suspicious activity
- [ ] Keep Docker and system packages updated

## Performance

### For Production

1. Use a production WSGI server (Gunicorn):

Update `Dockerfile`:
```dockerfile
# Install Gunicorn
RUN uv pip install gunicorn

# Update CMD
CMD ["uv", "run", "gunicorn", "sfexpress_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

2. Add caching (Redis):
```yaml
services:
  redis:
    image: redis:alpine
    restart: unless-stopped
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review configuration: `docker-compose config`
- Verify environment: `docker-compose exec web env`
