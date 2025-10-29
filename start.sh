#!/bin/bash

# Quick Start Script for SF Express API

echo "==================================="
echo "SF Express API - Quick Start"
echo "==================================="
echo ""

# Check if database exists
if [ ! -f "db.sqlite3" ]; then
    echo "Setting up database..."
    uv run python manage.py migrate
    uv run python manage.py load_sample_data
    echo ""
fi

# Offer to create superuser
echo "Would you like to create a superuser for the admin panel? (y/n)"
read -r create_superuser

if [ "$create_superuser" = "y" ]; then
    uv run python manage.py createsuperuser
    echo ""
fi

echo "Starting development server..."
echo ""
echo "API will be available at: http://localhost:8000/api/"
echo "Admin panel at: http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uv run python manage.py runserver
