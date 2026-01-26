# Ethiopian Domestic & Skilled Worker Platform

## Project Overview

This is a full-stack web application that connects households and businesses with domestic and skilled workers across Ethiopia. The platform serves as an online marketplace tailored specifically for the Ethiopian labor market, featuring Fayda ID integration, Ethiopian-inspired design, and comprehensive worker-employer matching capabilities. The system addresses the unique cultural, linguistic, and regulatory requirements of Ethiopia's domestic labor market.

## Architecture

The platform uses a decoupled architecture with:
- **Backend**: Django REST Framework
- **Frontend**: React/Next.js
- **Database**: PostgreSQL
- **Caching**: Redis

### Technology Stack

**Backend:**
- Django 4.2+ with Django REST Framework
- PostgreSQL 14+ for primary database
- Redis for caching and session management
- Celery for background tasks
- JWT for authentication
- Django Channels for real-time notifications

**Frontend:**
- Next.js 14+ with App Router
- React 18+ with TypeScript
- Tailwind CSS with custom Ethiopian design system
- React Query for state management
- React Hook Form for form handling
- Next.js Image optimization

**Infrastructure:**
- Docker containerization
- Nginx reverse proxy
- AWS S3 or local storage for file uploads
- PostgreSQL with proper indexing strategy

## Key Features

1. **Worker Profile Management**: Comprehensive profiles with skills, credentials, and Ethiopian-specific information
2. **Employer Job Management**: Job posting and search capabilities
3. **Advanced Search & Matching**: Filtering by region, skills, language, and other criteria
4. **Authentication & Authorization**: Role-based access control (Admin, Employer, Worker)
5. **Ethiopian Cultural Integration**: Localized design, languages, and cultural preferences
6. **Admin Panel**: Platform management and analytics
7. **Mobile-First Responsive Design**: Optimized for all devices
8. **Data Integration**: Validation and LMIS compatibility
9. **Communication System**: Notifications and messaging
10. **Performance & Scalability**: Optimized for Ethiopian internet conditions

## Building and Running

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis
- Poetry (for Python dependency management)
- Docker (optional)

### Poetry Installation
If you don't have Poetry installed:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Backend Setup with Poetry
```bash
# Install Python dependencies using Poetry
poetry install

# Activate the virtual environment
poetry shell

# Or run commands directly in the Poetry environment
poetry run python manage.py [command]

# Set up database
poetry run python manage.py migrate
poetry run python manage.py createsuperuser

# Run development server
poetry run python manage.py runserver
```

### Frontend Setup
```bash
# Install Node.js dependencies
cd frontend
npm install

# Run development server
npm run dev
```

### Using Docker
```bash
# Build and run the entire application
docker-compose up --build

# Run in detached mode
docker-compose up -d
```

## Development Conventions

### Code Style
- Follow PEP 8 for Python code
- Use TypeScript for type safety in frontend
- Follow Django best practices for model design
- Use consistent naming conventions aligned with requirements

### Dependency Management with Poetry
- All Python dependencies must be managed through Poetry
- Add new dependencies using `poetry add package-name`
- Add development dependencies using `poetry add --group dev package-name`
- Update the lock file after adding dependencies: `poetry lock`
- Document any new dependencies in the README.md file
- Always run commands within the Poetry environment: `poetry run command` or activate the shell with `poetry shell`

### Testing
- Write unit tests for all models and API endpoints
- Implement integration tests for critical workflows
- Follow the testing strategy outlined in the design document
- Maintain high test coverage especially for security and validation logic

### Ethiopian Cultural Considerations
- Ensure all Ethiopian regions, languages, and cultural elements are properly represented
- Validate all data against Ethiopian standards and formats (e.g., Fayda ID)
- Support Amharic and other local languages
- Follow Ethiopian design aesthetics and color schemas

### Security
- Implement proper authentication and authorization
- Validate all user inputs and file uploads
- Use secure password storage and JWT token management
- Ensure data privacy and protection of personal information

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/password-reset/` - Password reset

### Workers
- `GET /api/workers/` - List workers with filtering
- `POST /api/workers/` - Create worker profile
- `GET /api/workers/{id}/` - Get worker details
- `PUT /api/workers/{id}/` - Update worker profile
- `POST /api/workers/{id}/upload-photo/` - Upload profile photo
- `POST /api/workers/{id}/upload-certification/` - Upload certification

### Jobs
- `GET /api/jobs/` - List job postings
- `POST /api/jobs/` - Create job posting
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job posting
- `POST /api/jobs/{id}/shortlist/` - Shortlist worker

### Search
- `GET /api/search/workers/` - Advanced worker search
- `GET /api/search/jobs/` - Job search
- `GET /api/filters/` - Get available filter options

## Current Implementation Status

Based on the implementation plan in `tasks.md`, the project is in progress with:
- ✅ Project setup and core infrastructure
- ✅ Authentication system implementation
- ✅ Worker Profile model implementation
- 🔄 Remaining features in various stages of development

For the most up-to-date progress, refer to the `tasks.md` file which tracks the implementation status of all features.