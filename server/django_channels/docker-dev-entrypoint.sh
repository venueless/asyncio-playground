#!/bin/bash
# Start server
echo "Starting server"
cd /app/django_channels
python manage.py runserver 0.0.0.0:8375
