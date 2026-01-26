# Ethiopian Domestic & Skilled Worker Platform

## Project Setup with Poetry

This project uses Poetry for dependency management. Follow these steps to set up the project:

### Prerequisites

- Python 3.9+
- Poetry (installation instructions below)

### Installing Poetry

If you don't have Poetry installed, run:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Or follow the [official Poetry installation guide](https://python-poetry.org/docs/#installation).

### Setting up the Project

1. Clone the repository
2. Navigate to the project directory
3. Install dependencies:

```bash
poetry install
```

4. Activate the virtual environment:

```bash
poetry shell
```

Or run commands directly in the environment:

```bash
poetry run python manage.py [command]
```

### Running the Development Server

```bash
# With activated shell
poetry shell
python manage.py runserver

# Or without activating the shell
poetry run python manage.py runserver
```

### Managing Dependencies

- To add a new dependency: `poetry add package-name`
- To add a dev dependency: `poetry add --group dev package-name`
- To update dependencies: `poetry update`

### Database Setup

This project uses PostgreSQL. Before running migrations, ensure PostgreSQL is running and update environment variables as needed:

```bash
# Run database migrations
poetry run python manage.py migrate

# Create a superuser
poetry run python manage.py createsuperuser
```

### Creating Migrations

```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

### Running Tests

```bash
poetry run python manage.py test
```

### Project Structure

- `laborcon/` - Django project settings
- `users/` - User authentication and management app
- `workers/` - Worker profiles app
- `employers/` - Employer profiles app
- `jobs/` - Job posting app
- `static/` - Static files (CSS, JS, images)
- `media/` - User-uploaded files
- `templates/` - Django templates
- `pyproject.toml` - Poetry dependencies and project settings
- `poetry.lock` - Locked dependency versions