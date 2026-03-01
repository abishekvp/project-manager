# Quick Start Guide - Local Development

## Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd project-manager
```

### 2. Create Virtual Environment
```bash
python -m venv env
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your local database credentials
# For local development, you can use:
DEBUG=True
SECRET_KEY=your-dev-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit http://localhost:8000

## Local Database Setup (Optional - PostgreSQL)

### Install PostgreSQL
- Windows: https://www.postgresql.org/download/windows/
- macOS: `brew install postgresql`
- Linux: `sudo apt-get install postgresql`

### Create Database
```bash
psql -U postgres
CREATE DATABASE project_manager_db;
CREATE USER project_manager_user WITH PASSWORD 'your_password';
ALTER ROLE project_manager_user SET client_encoding TO 'utf8';
ALTER ROLE project_manager_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE project_manager_user SET default_transaction_deferrable TO on;
ALTER ROLE project_manager_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE project_manager_db TO project_manager_user;
\q
```

### Update .env
```
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=project_manager_db
DB_USER=project_manager_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Common Commands

### Database Operations
```bash
# Make migrations for changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show SQL for migration
python manage.py sqlmigrate app 0001
```

### Create/Manage Superuser
```bash
# Create new superuser
python manage.py createsuperuser

# Change password
python manage.py changepassword
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Serve static files in development (Django does this automatically)
```

### Utilities
```bash
# Open Python shell with Django context
python manage.py shell

# Run tests
python manage.py test

# Show all URLs
python manage.py show_urls
```

## Deployment Checklist

Before deploying to Render:

- [ ] Test locally with `DEBUG=False`
- [ ] Generate new SECRET_KEY: `python generate_secret_key.py`
- [ ] Update ALLOWED_HOSTS with your domain
- [ ] Ensure all environment variables are set on Render
- [ ] Test migrations run successfully
- [ ] Verify static files are collected
- [ ] Check database connection string
- [ ] Review security settings in settings.py
- [ ] Commit all changes to Git
- [ ] Push to GitHub/GitLab

See DEPLOYMENT.md for detailed Render deployment instructions.
