# Skate Project

A FastAPI backend for managing skate parks, events, and community features.

## Project Architecture

This project follows a domain-driven design approach with a clear separation of concerns:

### Domain-Driven Structure

```
app/
├── core/                      # Application core (config, exceptions, middleware)
│   ├── config/                # Configuration with environment-specific settings
│   ├── exceptions/            # Custom exception handlers
│   └── middleware/            # Middleware components
├── domain/                    # Domain-driven modules
│   ├── users/                 # User domain
│   │   ├── api/               # API routes for users
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── repositories/      # Data access layer
│   ├── parks/                 # Skate parks domain
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── repositories/
│   └── ...                    # Other domains
├── infrastructure/            # Infrastructure concerns
│   ├── database/              # Database setup and session management
│   ├── security/              # Authentication and authorization
│   └── cache/                 # Caching mechanisms (Redis)
└── api/                       # API layer
    ├── dependencies/          # Shared API dependencies
    ├── router.py              # Main API router
    └── v1/                    # API version 1
```

### Key Components

- **Domain Layer**: Contains business logic, models, and repositories for each domain
- **Infrastructure Layer**: Handles database connections, security, and caching
- **API Layer**: Manages API routes and dependencies

## Available Domains

### Users Domain

Handles user authentication, registration, and profile management.

### Parks Domain

Manages skate park information, features, photos, and ratings. See [Parks Domain Documentation](app/domain/parks/README.md) for details.

## Getting Started

### Prerequisites

1. **Python 3.12** (or higher)
2. **Poetry** (for dependency management)
3. **Make** (for task automation)
4. **Docker** and **Docker Compose** (for running databases)

### Installing Poetry

Follow the official installation guide for Poetry:

[Poetry Installation Guide](https://python-poetry.org/docs/#installing-with-the-official-installer)

Or Alternatively, the [PyCharm Poetry Installation Guide](https://www.jetbrains.com/help/pycharm/poetry.html)

### Installing Make

First, install Chocolatey (Windows package manager) by following this guide:

[Chocolatey Installation Guide](https://chocolatey.org/install)

Once Chocolatey is installed, you can install Make by running:

```bash
choco install make
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/tomlinc98/skate-project.git
cd skate-project
```

### 2. Start the Database Services

```bash
docker-compose up -d
```

This will start PostgreSQL and Redis services in Docker containers.

### 3. Install Dependencies

Once inside the project directory, run the following command to install the project dependencies using Poetry:

```bash
make install
```

This will install all the required dependencies for the project as defined in the pyproject.toml file.

### 4. Run Database Migrations

```bash
alembic upgrade head
```

This will apply all database migrations to create the necessary tables.

### 5. Set Up Pre-Commit Hooks

Install the pre-commit hooks to enforce code style and linting before each commit.

```bash
make install-pre-commit
```

You can also manually run `pre-commit` on all files:

```bash
make lint
```

### 6. Running the Application

```bash
make run
```

### 7. Accessing API Documentation

FastAPI provides automatic interactive API documentation. You can access it at:

http://127.0.0.1:8000/docs

## Development

### Creating New Migrations

After making changes to the database models, create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Then apply the migration:

```bash
alembic upgrade head
```

### Running Tests

```bash
make test
```

This will run all tests using pytest.
