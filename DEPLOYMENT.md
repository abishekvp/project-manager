# Deployment Guide for Render

## Prerequisites
- Render account (https://render.com)
- Django project with PostgreSQL
- GitHub repository with your code

## Steps to Deploy

### 1. Prepare Your Repository
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create PostgreSQL Database on Render
1. Go to Render Dashboard
2. Click "New" → "PostgreSQL"
3. Configure:
   - Name: `project-manager-db`
   - Database: `project_manager_db`
   - Username: `project_manager_user`
   - Region: Choose your preferred region
4. Copy the connection details for later

### 3. Set Environment Variables on Render
In your Render service settings, add these environment variables:

```
SECRET_KEY=<generate a new secure key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=project_manager_db
DB_USER=project_manager_user
DB_PASSWORD=<from database setup>
DB_HOST=<from database connection string>
DB_PORT=5432
```

### 4. Deploy Web Service
1. Create New Web Service from your GitHub repository
2. Configure:
   - Name: `project-manager`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn main.wsgi`
   - Auto-Deploy: On

### 5. Post-Deployment
After deployment, the release phase will run migrations automatically via the Procfile.

If you need to run custom commands, use the Render Shell:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `SECRET_KEY` | Django secret key | Auto-generated |
| `DEBUG` | Debug mode | `False` (always for production) |
| `ALLOWED_HOSTS` | Allowed domains | `yourdomain.com,www.yourdomain.com` |
| `DB_NAME` | Database name | `project_manager_db` |
| `DB_USER` | Database user | `project_manager_user` |
| `DB_PASSWORD` | Database password | Secure password |
| `DB_HOST` | Database host | `dpg-xxxxx.render.com` |
| `DB_PORT` | Database port | `5432` |

## Security Best Practices

- ✅ All secrets are stored in Render environment variables
- ✅ DEBUG is set to False in production
- ✅ HTTPS is enabled by default
- ✅ CSRF protection is enabled
- ✅ Secure cookies are configured
- ✅ HSTS headers are set

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL in Render settings
- Check PostgreSQL service is running
- Review logs in Render Dashboard

### Static Files Not Loading
- Ensure `STATIC_ROOT` is correctly configured
- Run `python manage.py collectstatic --noinput`
- Check that whitenoise is in MIDDLEWARE

### Migration Errors
- Check Render logs for specific errors
- Use Render Shell to run migrations manually
- Review model definitions for conflicts
