#!/bin/bash
set -e

echo "======================================"
echo "SF Express API - Docker Entrypoint"
echo "======================================"
echo ""

# Ensure data directory exists
mkdir -p /data

# Wait for a moment to ensure everything is ready
sleep 2

# Run database migrations
echo "Running database migrations..."
uv run python manage.py migrate --noinput

# Setup admin user (runs on every deployment)
echo "Setting up admin user..."
uv run python manage.py setup_admin

# Check if database is empty (first run)
if [ ! -f /data/.initialized ]; then
    echo "First run detected, loading SF Express location data..."
    uv run python manage.py load_sfexpress_data

    # Mark as initialized
    touch /data/.initialized
    echo "SF Express location data loaded successfully!"
else
    echo "Database already initialized, skipping data loading..."
fi

echo ""
echo "======================================"
echo "Starting SF Express API Server"
echo "======================================"
echo ""

# Execute the main command
exec "$@"
