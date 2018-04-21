#!/bin/sh
# Build all containers
# Images are automatically fetched, if necessary, from docker hub
docker-compose build

# Start a new web container to run migrations
# Use --rm to remove the container when the command completes
docker-compose run --rm app /venv/bin/python /code/monthly_expenses/manage.py migrate

# Run everything in the background with -d
docker-compose up -d