# Deployment Guide

This guide provides instructions for deploying the Ethiopian Domestic & Skilled Worker Platform to a production environment.

## Prerequisites

*   Docker and Docker Compose
*   A server with a public IP address
*   A domain name pointed to the server's IP address
*   A PostgreSQL database
*   A Redis instance
*   An email server (e.g., SendGrid, Mailgun)
*   A Sentry account for error tracking

## 1. Environment Variables

Create a `.env` file in the `backend` directory with the following environment variables:

```
SECRET_KEY=<your secret key>
FIELD_ENCRYPTION_KEY=<your fernet key>
DEBUG=False
ALLOWED_HOSTS=<your domain name>,www.<your domain name>
DATABASE_URL=postgres://<user>:<password>@<host>:<port>/<dbname>
REDIS_URL=redis://<host>:<port>/0
SENTRY_DSN=<your sentry dsn>
EMAIL_HOST=<your email host>
EMAIL_PORT=<your email port>
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your email user>
EMAIL_HOST_PASSWORD=<your email password>
```

Replace the values in `<...>` with your actual configuration.

## 2. Build and Run the Application

Use the production Docker Compose file to build and run the application:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

This will start the following services:

*   `web`: The Django application running with Gunicorn.
*   `nginx`: An Nginx reverse proxy that serves static files and proxies requests to the `web` service.
*   `db`: The PostgreSQL database.
*   `redis`: The Redis instance.

## 3. Database Migrations

Run the database migrations:

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

## 4. Create a Superuser

Create a superuser to access the Django admin interface:

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## 5. Collect Static Files

Collect the static files:

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
```

## 6. SSL/TLS with Let's Encrypt

To enable SSL/TLS, you can use Certbot with the Nginx plugin.

1.  Install Certbot and the Nginx plugin on your server.
2.  Stop the `nginx` service:

    ```bash
    docker-compose -f docker-compose.prod.yml stop nginx
    ```

3.  Run Certbot to obtain a certificate:

    ```bash
    sudo certbot --nginx -d <your domain name> -d www.<your domain name>
    ```

4.  Certbot will modify your `nginx.conf` file to include the SSL/TLS configuration. You will need to copy the updated configuration to your `nginx.conf` file.

5.  Restart the `nginx` service:

    ```bash
    docker-compose -f docker-compose.prod.yml up -d nginx
    ```

## 7. Monitoring

The application is configured with a health check endpoint at `/health/`. You can use a monitoring service like Uptime Robot or Pingdom to monitor this endpoint.

Error tracking is configured with Sentry. Make sure you have provided a valid `SENTRY_DSN` in your `.env` file.
