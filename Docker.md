# Docker Setup for Ethiopian Domestic & Skilled Worker Platform

This project includes Docker configurations for both development and production environments following industry best practices.

## Prerequisites

- Docker Engine (v20.10 or later)
- Docker Compose (v2.0 or later)

## Development Environment

### Quick Start

1. Navigate to the project root directory:
   ```bash
   cd /path/to/chilota
   ```

2. Build and start the services:
   ```bash
   docker-compose up --build
   ```

3. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - MailHog (for email testing): http://localhost:8025

### Services

The development setup includes:
- **Backend**: Django application running on port 8000
- **Frontend**: Next.js application running on port 3000
- **Database**: PostgreSQL (internal access only)
- **Cache**: Redis (internal access only)
- **Email Testing**: MailHog for capturing outgoing emails

### Running Management Commands

To run Django management commands, use:
```bash
# Create a superuser
docker-compose exec backend python manage.py createsuperuser

# Run tests
docker-compose exec backend python manage.py test

# Create migrations
docker-compose exec backend python manage.py makemigrations

# Apply migrations (usually done automatically on startup)
docker-compose exec backend python manage.py migrate
```

## Production Environment

### Setup

1. Create a `.env` file in the project root with your production environment variables:
   ```bash
   DJANGO_SECRET_KEY=your_very_long_secret_key_here
   FIELD_ENCRYPTION_KEY=your_32_byte_base64_encoded_key_here
   DB_PASSWORD=your_secure_db_password
   DATABASE_URL=postgresql://chilota_user:your_secure_db_password@db:5432/chilota_db
   EMAIL_HOST=smtp.your-provider.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=true
   EMAIL_HOST_USER=your_email@domain.com
   EMAIL_HOST_PASSWORD=your_email_password
   SENTRY_DSN=https://your-sentry-dsn-if-using-sentry
   CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   FRONTEND_API_BASE_URL=https://api.yourdomain.com/api
   ```

2. Create SSL certificate directories:
   ```bash
   mkdir -p nginx/ssl
   # Add your SSL certificates to nginx/ssl/
   ```

3. Build and start the production services:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

### Production Notes

- The setup uses multi-stage Docker builds for optimized images
- Security is enhanced with non-root users and minimal base images
- Environment variables are loaded from the `.env` file
- SSL termination is handled by Nginx
- Internal services (database, cache) are not exposed to host

## Multi-Stage Builds

Both backend and frontend use multi-stage builds to:
- Separate build dependencies from runtime dependencies
- Reduce final image size
- Improve security by excluding build tools from production images
- Enable faster rebuilds through layer caching

### Backend Build Stages
1. **Builder Stage**: Installs build dependencies and Python packages
2. **Runtime Stage**: Copies only necessary files and runs as non-root user

### Frontend Build Stages
1. **Dependencies Stage**: Installs Node.js packages
2. **Builder Stage**: Builds the Next.js application
3. **Runtime Stage**: Serves the built application as non-root user

## Useful Commands

### Development Commands

- View logs: `docker-compose logs -f`
- Stop services: `docker-compose down`
- Stop and remove volumes: `docker-compose down -v`
- Run specific service: `docker-compose up backend`

### Production Commands

- View logs: `docker-compose -f docker-compose.prod.yml logs -f`
- Stop services: `docker-compose -f docker-compose.prod.yml down`
- Scale services: `docker-compose -f docker-compose.prod.yml up --scale backend=3 -d`

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Make sure ports 80, 443, 3000, 8000, 5432, and 6379 are available.

2. **Permission Issues**: On Linux, you might need to run Docker commands with `sudo`.

3. **Database Connection Errors**: Ensure the database service is healthy before the backend starts.

4. **Migration Issues**: If you encounter migration issues, try running migrations manually:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

### Health Checks

Services include health checks to ensure proper startup sequence:
- PostgreSQL: Checked with `pg_isready`
- Redis: Checked with `redis-cli ping`
- Backend and Frontend: Depend on their respective upstream services

## Environment Variables

### Required for Development

The development environment uses default values for most environment variables, but you can override them by creating a `.env` file in the project root.

### Required for Production

For production, you must provide secure values for:
- `DJANGO_SECRET_KEY`
- `FIELD_ENCRYPTION_KEY`
- `DB_PASSWORD`
- Email configuration variables
- CORS_ALLOWED_ORIGINS