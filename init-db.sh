#!/bin/bash
# Script to initialize the database with sample data for development

echo "Starting database initialization..."

# Wait for the database to be ready
echo "Waiting for database to be ready..."
for i in {1..30}; do
    if docker-compose exec db pg_isready > /dev/null 2>&1; then
        echo "Database is ready!"
        break
    fi
    echo "Waiting for database... ($i/30)"
    sleep 2
done

# Run migrations
echo "Running migrations..."
docker-compose exec backend python manage.py migrate

# Create a superuser (with default credentials for development)
echo "Creating superuser..."
docker-compose exec backend python manage.py createsuperuser --noinput --username admin --email admin@example.com || echo "Superuser may already exist"

# Load sample data if available
if [ -f "./backend/fixtures/sample_data.json" ]; then
    echo "Loading sample data..."
    docker-compose exec backend python manage.py loaddata sample_data.json
else
    echo "No sample data fixture found. Skipping."
fi

# Collect static files
echo "Collecting static files..."
docker-compose exec backend python manage.py collectstatic --no-input

echo "Database initialization completed!"
echo ""
echo "Access the application:"
echo "- Frontend: http://localhost:3000"
echo "- Backend Admin: http://localhost:8000/admin (login: admin/admin123)"
echo "- MailHog: http://localhost:8025"