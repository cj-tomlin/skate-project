# Getting Started

## Prerequisites

1. **Python 3.12** (or higher)
2. **Poetry** (for dependency management)
3. **Make** (for task automation)

### Installing Poetry

Follow the official installation guide for Poetry:

[Poetry Installation Guide](https://python-poetry.org/docs/#installing-with-the-official-installer)

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

### 2. Install Dependencies

Once inside the project directory, run the following command to install the project dependencies using Poetry:

```bash
git clone https://github.com/tomlinc98/skate-project.git
cd skate-project
```

This will install all the required dependencies for the project as defined in the pyproject.toml file.

### 3. Set Up Pre-Commit Hooks

```bash
make install-pre-commit
```

Pre-Commit is used to enforce code quality through automatic linting and formatting checks.

### 4. Running the Application

```bash
make run
```

### 5. Accessing API Documentation

FastAPI provides automatic interactive API documentation. You can access it at:

http://127.0.0.1:8000/docs
