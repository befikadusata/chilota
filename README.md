# Ethiopian Domestic & Skilled Worker Platform

A full-stack web application connecting households and businesses with domestic and skilled workers across Ethiopia. The platform serves as an online marketplace tailored specifically for the Ethiopian labor market, featuring Fayda ID integration, Ethiopian-inspired design, and comprehensive worker-employer matching capabilities.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Docker Setup](#docker-setup)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Worker Profile Management**: Comprehensive profiles with skills, credentials, and Fayda ID integration
- **Employer Job Management**: Job posting and worker search capabilities
- **Advanced Search & Matching**: Filtering by region, skills, language, experience, and other criteria
- **Ethiopian Cultural Integration**: Localized design with Ethiopian colors, languages, and cultural considerations
- **Admin Panel**: Comprehensive management tools for platform oversight
- **Mobile-First Responsive Design**: Optimized for smartphones and various screen sizes
- **Communication System**: Notifications and secure messaging between users
- **Authentication & Authorization**: JWT-based authentication with role-based access control

## Tech Stack

### Backend
- **Framework**: Django 4.x with Django REST Framework
- **API**: Django Ninja for API endpoints
- **Database**: PostgreSQL with dj_database_url
- **Authentication**: JWT with refresh token rotation
- **Caching**: Redis
- **File Storage**: Local media storage with security validation
- **Logging**: Comprehensive logging with audit trails
- **Dependency Management**: Poetry

### Frontend
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: Radix UI primitives
- **Icons**: Lucide React
- **Forms**: React Hook Form with Zod validation
- **State Management**: Client-side state management
- **Data Fetching**: TanStack Query

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Monitoring**: Sentry (optional)
- **Email**: SMTP with configurable providers

## Prerequisites

- **Backend**:
  - Python 3.9+
  - Poetry
  - PostgreSQL
  - Redis (for caching)

- **Frontend**:
  - Node.js 18+
  - npm, yarn, pnpm, or bun

- **Infrastructure**:
  - Docker Engine (v20.10+) and Docker Compose (v2.0+) (for containerized setup)

## Getting Started

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

4. Create a `.env` file with the following variables:
   ```env
   SECRET_KEY=your_secret_key_here
   FIELD_ENCRYPTION_KEY=your_32_byte_base64_encoded_key_here
   DEBUG=True
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   REDIS_URL=redis://localhost:6379/0
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

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

3. Create a `.env.local` file with the following variables:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
   ```

4. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   # or
   bun dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser to see the result.

## Docker Setup

The project includes comprehensive Docker configurations for both development and production environments.

### Development with Docker

1. From the project root, build and start all services:
   ```bash
   docker-compose up --build
   ```

2. Initialize the database with sample data:
   ```bash
   ./init-db.sh
   ```

3. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - MailHog (for email testing): http://localhost:8025

### Production with Docker

1. Create a `.env` file in the project root with production environment variables
2. Build and start the production services:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

For detailed Docker setup instructions, see the [Docker.md](Docker.md) file.

## Project Structure

```
chilota/
├── backend/                 # Django backend application
│   ├── apps/                # Django apps (users, workers, employers, jobs, etc.)
│   ├── core/                # Django project settings and configuration
│   ├── static/              # Static files (CSS, JS, images)
│   ├── templates/           # Django templates
│   ├── media/               # User-uploaded files
│   ├── requirements/        # Poetry dependency files
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions and helpers
│   ├── manage.py            # Django management script
│   └── README.md            # Backend documentation
├── frontend/                # Next.js frontend application
│   ├── app/                 # Next.js app router pages
│   ├── components/          # Reusable React components
│   ├── hooks/               # Custom React hooks
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies and scripts
│   └── README.md            # Frontend documentation
├── docs/                    # Project documentation
├── docker-compose.yml       # Docker Compose for development
├── docker-compose.prod.yml  # Docker Compose for production
├── Docker.md                # Docker setup documentation
└── README.md                # This file
```

## API Documentation

The backend API is documented using Django Ninja. API endpoints can be explored at:
- http://localhost:8000/api/docs (when running the development server)

## Testing

### Backend Testing

Run Django tests:
```bash
# With Poetry shell activated
python manage.py test

# Or without activating the shell
poetry run python manage.py test
```

### Frontend Testing

Run frontend tests:
```bash
# In the frontend directory
npm run test
# or
yarn test
# or
pnpm test
```

## Deployment

### Production Deployment

The application is designed for containerized deployment using Docker. For production:

1. Use the production Docker Compose configuration
2. Configure environment variables for production
3. Set up SSL certificates for HTTPS
4. Configure a reverse proxy (Nginx recommended)
5. Set up a production database and Redis instance
6. Implement proper logging and monitoring solutions

### Environment Variables

Both backend and frontend require environment variables for configuration. See the setup sections above for required variables.

## Contributing

We welcome contributions to the Ethiopian Domestic & Skilled Worker Platform! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the Ethiopian labor market with cultural sensitivity and local requirements in mind
- Inspired by the need for formal connections between workers and employers in Ethiopia
- Designed with scalability and maintainability in mind