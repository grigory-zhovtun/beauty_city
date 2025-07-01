#!/bin/bash

echo "Fixing database issues..."

# Backup the current database (just in case)
echo "Creating backup of current database..."
cp db.sqlite3 db.sqlite3.backup

# Remove the current database
echo "Removing current database..."
rm db.sqlite3

# Create a new database and apply migrations
echo "Creating new database and applying migrations..."
python manage.py migrate

echo "Database has been reset and migrations applied."
echo "You may need to recreate your superuser with: python manage.py createsuperuser"