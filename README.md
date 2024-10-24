# Getting Started

## Prerequisites

1. **Python 3.12** (or higher)
2. **Poetry** (for dependency management)
3. **Make** (for task automation)

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

### 2. Install Dependencies

Once inside the project directory, run the following command to install the project dependencies using Poetry:

```bash
make install
```

This will install all the required dependencies for the project as defined in the pyproject.toml file.

### 3. Set Up Pre-Commit Hooks

Install the pre-commit hooks to enforce code style and linting before each commit.

```bash
make install-pre-commit
```

You can also manually run `pre-commit` on all files:

```bash
make lint
```

### 4. Running the Application

```bash
make run
```

### 5. Accessing API Documentation

FastAPI provides automatic interactive API documentation. You can access it at:

http://127.0.0.1:8000/docs
