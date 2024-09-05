#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Activate the virtual environment
source /env/bin/activate

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Run the appropriate command based on the input argument
if [ "$1" == 'gunicorn' ]; then
    exec gunicorn django_invoice.wsgi:application -b 0.0.0.0:8000
else
    exec python manage.py runserver 0.0.0.0:8000
fi
