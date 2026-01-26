# Ethiopian Domestic & Skilled Worker Platform

## Project Overview

This is a full-stack web application that connects households and businesses with domestic and skilled workers across Ethiopia. The platform serves as an online marketplace tailored specifically for the Ethiopian labor market, featuring Fayda ID integration, Ethiopian-inspired design, and comprehensive worker-employer matching capabilities.

The system addresses the unique cultural, linguistic, and regulatory requirements of Ethiopia's domestic labor market. It consists of a Django-based backend API and a Next.js frontend application.

### Architecture

The project follows a modern full-stack architecture:

- **Backend**: Django REST API with Django Ninja for API endpoints, PostgreSQL database, and JWT authentication
- **Frontend**: Next.js 16 application with TypeScript, Tailwind CSS, and Radix UI components
- **Database**: PostgreSQL with dj_database_url for connection management
- **Authentication**: JWT-based authentication with refresh token rotation
- **File Storage**: Local media storage with upload validation and security
- **Caching**: Redis integration for improved performance
- **Logging**: Comprehensive logging with audit trails

### Key Features

1. **Worker Profile Management**: Comprehensive profiles with skills, credentials, and Fayda ID integration
2. **Employer Job Management**: Job posting and worker search capabilities
3. **Advanced Search & Matching**: Filtering by region, skills, language, experience, and other criteria
4. **Ethiopian Cultural Integration**: Localized design with Ethiopian colors, languages, and cultural considerations
5. **Admin Panel**: Comprehensive management tools for platform oversight
6. **Mobile-First Responsive Design**: Optimized for smartphones and various screen sizes
7. **Communication System**: Notifications and secure messaging between users

## Building and Running

### Backend Setup (Django)

The backend uses Poetry for dependency management.

#### Prerequisites
- Python 3.9+
- Poetry
- PostgreSQL
- Redis (for caching)

#### Installation
1. Navigate to the `/backend` directory
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

#### Environment Configuration
Create a `.env` file in the backend root with the following variables:
```
SECRET_KEY=your_secret_key_here
FIELD_ENCRYPTION_KEY=your_fernet_key_here
DEBUG=True
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Database Setup
1. Run database migrations:
   ```bash
   python manage.py migrate
   ```
2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

#### Running the Development Server
```bash
# With activated shell
poetry shell
python manage.py runserver

# Or without activating the shell
poetry run python manage.py runserver
```

### Frontend Setup (Next.js)

#### Prerequisites
- Node.js 18+ (recommended)
- npm, yarn, pnpm, or bun

#### Installation
1. Navigate to the `/frontend` directory
2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   # or
   bun install
   ```

#### Environment Configuration
Create a `.env.local` file in the frontend root with the following variables:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

#### Running the Development Server
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Development Conventions

### Backend (Django)
- Use Poetry for dependency management
- Follow PEP 8 coding standards
- Use Django's built-in form validation and model validation
- Implement proper error handling and logging
- Use Django's internationalization framework for multi-language support
- Follow Django REST Framework best practices for API development
- Use Django Ninja for API endpoints where appropriate

### Frontend (Next.js)
- Use TypeScript for type safety
- Follow React best practices and hooks conventions
- Use Tailwind CSS for styling with the project's design system
- Implement responsive design for all device sizes
- Use Radix UI components for accessibility
- Follow Next.js file-based routing conventions
- Implement proper error boundaries and loading states

### Testing
- Backend: Use Django's testing framework
- Frontend: Use Jest and React Testing Library
- Write unit tests for critical business logic
- Implement integration tests for API endpoints

### Code Quality
- Use ESLint and Prettier for consistent code formatting
- Implement proper type checking with TypeScript
- Follow security best practices for user data protection
- Use environment variables for configuration management

## Project Structure

### Backend Structure
```
backend/
├── apps/                 # Django apps (users, workers, employers, jobs, etc.)
├── core/                 # Django project settings and configuration
├── static/               # Static files (CSS, JS, images)
├── templates/            # Django templates
├── media/                # User-uploaded files
├── requirements/         # Poetry dependency files
├── services/             # Business logic services
├── utils/                # Utility functions and helpers
├── manage.py             # Django management script
├── pyproject.toml        # Poetry configuration
└── README.md             # Backend documentation
```

### Frontend Structure
```
frontend/
├── app/                  # Next.js app router pages
├── components/           # Reusable React components
├── hooks/                # Custom React hooks
├── public/               # Static assets
├── package.json          # Node.js dependencies and scripts
├── next.config.ts        # Next.js configuration
├── tailwind.config.ts    # Tailwind CSS configuration
└── tsconfig.json         # TypeScript configuration
```

## Deployment

The application is designed to be deployed with Docker containers for both backend and frontend. The backend includes production-ready configurations with Gunicorn and Nginx.

### Docker Setup

The project includes comprehensive Docker configurations for both development and production environments:

1. **Development Environment**:
   - Docker Compose configuration with services for backend, frontend, PostgreSQL, Redis, and MailHog
   - Hot reloading for development
   - Easy database initialization script

2. **Production Environment**:
   - Production-grade Docker Compose with security enhancements
   - Non-root users for containers
   - Environment variable management
   - SSL support via Nginx

#### Running with Docker

For development:
```bash
# Build and start all services
docker-compose up --build

# Initialize the database with sample data
./init-db.sh
```

For production:
```bash
# Create .env file with production variables
# Then start the services
docker-compose -f docker-compose.prod.yml up --build -d
```

See the Docker.md file for complete documentation on Docker setup and usage.

For production deployment:
1. Use the provided Dockerfile.prod for production builds
2. Configure environment variables for production
3. Set up SSL certificates for HTTPS
4. Configure a reverse proxy (Nginx recommended)
5. Set up a production database and Redis instance
6. Implement proper logging and monitoring solutions