# Project Manager - Django Application

## Overview

A comprehensive Django project management application with role-based access control, project tracking, and team management capabilities.

## Features

- **Role-Based Access Control**: Lead, Manager, Peer, Vendor, and Administrator roles
- **Project Management**: Create, manage, and track projects
- **Task Management**: Assign and track tasks across projects
- **Team Collaboration**: Manage team members and permissions
- **Email Integration**: Configured SMTP mail server support
- **Lead Management**: Comprehensive lead tracking system
- **Marketing Tools**: Lead and marketing campaign management
- **API**: RESTful API for external integrations
- **Admin Dashboard**: Comprehensive administration panel

## Project Structure

```
project-manager/
├── administer/           # Administrator module
├── api/                 # REST API endpoints
├── app/                 # Core application logic
├── lead/                # Lead management
├── main/                # Django project settings
├── manager/             # Project manager module
├── marketing/           # Marketing tools
├── peer/                # Peer collaboration
├── vendor/              # Vendor management
├── static/              # CSS, JavaScript, Images
├── template/            # HTML templates
├── utils/               # Utility functions
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── db.sqlite3          # Development database
```

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (for production)
- Git

### Local Development Setup

See [QUICKSTART.md](QUICKSTART.md) for detailed local setup instructions.

```bash
# Clone repository
git clone <repository-url>
cd project-manager

# Create virtual environment
python -m venv env
source env/bin/activate  # or `env\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your local settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit http://localhost:8000

## Deployment

### Render Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete Render deployment instructions.

Quick summary:
1. Push code to GitHub
2. Create PostgreSQL database on Render
3. Create Web Service from GitHub repository
4. Configure environment variables
5. Deploy!

### Environment Variables

Key environment variables for production:

```
SECRET_KEY              # Django secret key (auto-generated or provided)
DEBUG                   # Set to False for production
ALLOWED_HOSTS           # Comma-separated list of allowed domains
DB_ENGINE              # Database backend (postgresql for production)
DB_NAME                # Database name
DB_USER                # Database user
DB_PASSWORD            # Database password
DB_HOST                # Database host
DB_PORT                # Database port (5432 for PostgreSQL)
```

See `.env.example` for complete list of available environment variables.

## Development

### Running Tests

```bash
python manage.py test
python manage.py test app.tests.TestModuleName
```

### Database Migrations

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration SQL
python manage.py sqlmigrate app 0001
```

### Django Admin

Access the Django admin panel at http://localhost:8000/admin/

### Shell Access

```bash
python manage.py shell
```

## Security

Production deployment includes:
- ✅ HTTPS enforced (SECURE_SSL_REDIRECT)
- ✅ Secure cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- ✅ XSS protection (SECURE_BROWSER_XSS_FILTER)
- ✅ HSTS headers (Strict-Transport-Security)
- ✅ Frame protection (X_FRAME_OPTIONS = 'DENY')
- ✅ CSRF protection enabled
- ✅ Environment-based secrets management
- ✅ Debug disabled in production

## Database

### Development
- Default: SQLite (db.sqlite3)
- Optional: PostgreSQL for testing production setup

### Production
- PostgreSQL on Render
- Connection pooling configured
- Automated backups (Render feature)

## Performance

- WhiteNoise for static file serving
- Gunicorn WSGI server in production
- Database query optimization
- Caching strategies implemented

## Logging

Logs are configured with:
- Console output for real-time monitoring
- File rotation (15MB per file, 10 backups)
- Separate loggers for Django, database queries, and requests
- Verbose formatting for debugging

Logs are stored in `logs/django.log`

## Support & Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Render Documentation](https://render.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## License

[Add your license information here]

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Contact

[Add your contact information here]
