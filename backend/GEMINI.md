# GEMINI.md

## Project Overview

This project is a Django-based web application called "Ethiopian Domestic & Skilled Worker Platform". Its purpose is to connect households and businesses in Ethiopia with domestic and skilled workers.

The project is built with the following technologies:

*   **Backend:** Django, Django REST Framework
*   **Dependency Management:** Poetry
*   **Database:** PostgreSQL (with SQLite for development - *inferred from common Django practices, not explicitly stated in README*)
*   **Authentication:** JSON Web Tokens (JWT) using `djangorestframework-simplejwt` (*inferred from prior knowledge of typical Django REST API setups, often mentioned in API sections if available*)

The project is divided into several Django apps:

*   `laborcon/` - Django project settings
*   `users/` - User authentication and management app
*   `workers/` - Worker profiles app
*   `employers/` - Employer profiles app
*   `jobs/` - Job posting app

## Building and Running

### Prerequisites

*   Python 3.9+
*   Poetry

### Setup

1.  **Install dependencies:**
    ```bash
    poetry install
    ```

2.  **Activate the virtual environment:**
    ```bash
    poetry shell
    ```

3.  **Run database migrations:**
    ```bash
    poetry run python manage.py migrate
    ```

4.  **Create a superuser:**
    ```bash
    poetry run python manage.py createsuperuser
    ```

### Running the Development Server

```bash
poetry run python manage.py runserver
```

### Running Tests

```bash
poetry run python manage.py test
```

## Development Conventions

*   **Dependency Management:** Project dependencies are managed with Poetry.
*   **Testing:** `pytest` and `pytest-django` are used for testing. (*inferred from common Django testing practices, though `README` only mentions `python manage.py test`*)
*   **API:** The project likely provides a RESTful API built with Django REST Framework. (*inferred from project type*)
*   **Authentication:** API authentication is likely handled by JWT. (*inferred from project type*)