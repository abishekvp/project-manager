# Environment Variables Reference

This document explains all environment variables used by the Django application.

## Required Variables for Production

### Django Core

| Variable | Purpose | Example | Required |
|----------|---------|---------|----------|
| `SECRET_KEY` | Django's secret key for cryptographic functions | `django-insecure-...` (generate with `python generate_secret_key.py`) | ✅ Yes |
| `DEBUG` | Debug mode toggle | `False` (always False in production) | ✅ Yes |
| `ALLOWED_HOSTS` | Comma-separated list of allowed domains | `yourdomain.com,www.yourdomain.com` | ✅ Yes |

### Database Configuration

| Variable | Purpose | Example | Required |
|----------|---------|---------|----------|
| `DB_ENGINE` | Database backend | `django.db.backends.postgresql` | ✅ Yes |
| `DB_NAME` | Database name | `project_manager_db` | ✅ Yes |
| `DB_USER` | Database user | `project_manager_user` | ✅ Yes |
| `DB_PASSWORD` | Database password | `secure-password-here` | ✅ Yes |
| `DB_HOST` | Database host | `dpg-xxxxx.render.com` | ✅ Yes |
| `DB_PORT` | Database port | `5432` | ✅ Yes (default: 5432) |

### Email Configuration (Optional)

| Variable | Purpose | Example | Required |
|----------|---------|---------|----------|
| `EMAIL_BACKEND` | Email backend | `django.core.mail.backends.smtp.EmailBackend` | ❌ No |
| `EMAIL_HOST` | SMTP server host | `smtp.gmail.com` | ❌ No |
| `EMAIL_PORT` | SMTP port | `587` | ❌ No |
| `EMAIL_USE_TLS` | Use TLS encryption | `True` | ❌ No |
| `EMAIL_HOST_USER` | SMTP username | `your-email@gmail.com` | ❌ No |
| `EMAIL_HOST_PASSWORD` | SMTP password | `app-specific-password` | ❌ No |

### Application Settings

| Variable | Purpose | Example | Required |
|----------|---------|---------|---------|
| `TIME_ZONE` | Application timezone | `Asia/Kolkata` | ❌ No |
| `LANGUAGE_CODE` | Default language | `en-us` | ❌ No |
| `SECURE_SSL_REDIRECT` | Force HTTPS | `True` | ❌ No |
| `SESSION_COOKIE_SECURE` | Secure session cookies | `True` | ❌ No |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies | `True` | ❌ No |

## Configuration by Environment

### Development (.env)
```
DEBUG=True
SECRET_KEY=django-insecure-dev-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### Staging (Render Environment Variables)
```
DEBUG=False
SECRET_KEY=<generated-secure-key>
ALLOWED_HOSTS=staging.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=project_manager_staging_db
DB_USER=<staging-user>
DB_PASSWORD=<staged-password>
DB_HOST=<staging-postgres-host>
DB_PORT=5432
```

### Production (Render Environment Variables)
```
DEBUG=False
SECRET_KEY=<generated-secure-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=project_manager_db
DB_USER=<production-user>
DB_PASSWORD=<production-password>
DB_HOST=<production-postgres-host>
DB_PORT=5432
```

## Generating SECRET_KEY

```bash
python generate_secret_key.py
```

This generates a cryptographically secure random key. Use a different key for each environment.

## Security Best Practices

### Do's ✅
- [x] Generate unique SECRET_KEY for each environment
- [x] Use strong, random passwords for database credentials
- [x] Store all secrets in environment variables (never commit to git)
- [x] Use HTTPS in production (DEBUG=False)
- [x] Rotate secrets regularly
- [x] Use app-specific passwords for Gmail/email services
- [x] Keep .env file in .gitignore

### Don'ts ❌
- [ ] Don't commit .env file to git
- [ ] Don't use same SECRET_KEY across environments
- [ ] Don't leave DEBUG=True in production
- [ ] Don't store credentials in code
- [ ] Don't share .env files via unencrypted channels
- [ ] Don't use weak passwords
- [ ] Don't expose DATABASE_URL in logs

## Setting Variables on Render

### Via Dashboard
1. Go to Service Settings
2. Navigate to Environment
3. Add each variable with its value
4. Click "Save Changes"
5. Service will redeploy with new variables

### Via Render CLI (if available)
```bash
render env:set SECRET_KEY=your-secret-key
render env:set DEBUG=False
# etc...
```

## Validating Configuration

After deploying, verify settings:

```bash
# Via Render Shell
python manage.py shell

# Check configuration
from django.conf import settings
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"Database: {settings.DATABASES['default']}")
```

## Troubleshooting

### Missing Variables Error
**Error**: `KeyError: 'VARIABLE_NAME'`
**Solution**: Add the variable to Render environment variables

### Database Connection Failed
**Error**: `psycopg.OperationalError: could not translate host name`
**Solution**: Verify DB_HOST is correct from Render PostgreSQL connection string

### DEBUG=False Issues
**Error**: Blank page or "Page not found"
**Solution**: 
- Add your domain to ALLOWED_HOSTS
- Check ALLOWED_HOSTS format (comma-separated without spaces)

## Testing Variables Locally

Create `.env` file (not committed):
```
# Copy from .env.example
cp .env.example .env

# Edit with your values
nano .env  # or use your editor

# Load and test
python manage.py validate
```

## Rotating Secrets

### Update SECRET_KEY
1. Generate new key: `python generate_secret_key.py`
2. Update in Render environment
3. Sessions will be invalidated (users will need to re-login)

### Update Database Password
1. Change password in PostgreSQL
2. Update DB_PASSWORD in Render
3. Re-deploy service
4. Verify connectivity works

### Update Email Credentials
1. Generate new app password in email provider
2. Update EMAIL_HOST_PASSWORD in Render
3. Test email functionality

## Additional Resources

- [Django Settings Documentation](https://docs.djangoproject.com/en/4.2/topics/settings/)
- [Environment Variables Best Practices](https://12factor.net/config)
- [Render Documentation](https://render.com/docs)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect-string.html)
