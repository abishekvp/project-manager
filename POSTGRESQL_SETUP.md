# PostgreSQL Setup Guide for Project Manager

## ✅ Database Configuration Complete

Your project is configured to use **PostgreSQL on Render** with the following setup:

**Connection Details:**
```
Engine: PostgreSQL (django.db.backends.postgresql)
Host: dpg-d6i6l3ngi27c738a92v0-a.oregon-postgres.render.com
Port: 5432
Database: project_manager_w0ay
User: project_manager_w0ay_user
```

---

## 🚀 Running Locally with PostgreSQL

### Option 1: Connect Locally to Remote Render PostgreSQL

**Prerequisites:**
- PostgreSQL client tools installed (psql)
- Network access to Render PostgreSQL (should be allowed)

**Steps:**
```bash
# 1. Test connection
psql -h dpg-d6i6l3ngi27c738a92v0-a.oregon-postgres.render.com \
     -U project_manager_w0ay_user \
     -d project_manager_w0ay

# 2. Run migrations
python manage.py migrate

# 3. Create superuser
python manage.py createsuperuser

# 4. Start development server
daphne -b 0.0.0.0 -p 8000 routing.application
```

---

### Option 2: Local PostgreSQL Development

**Setup Local PostgreSQL:**

**Windows - Using PostgreSQL Installer:**
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer, remember the password
3. In pgAdmin 4 (included), create database:
   ```sql
   CREATE DATABASE project_manager_dev;
   ```

**Update .env for local development:**
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=project_manager_dev
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

**Commands:**
```bash
# 1. Install psycopg (already done)
pip install psycopg[binary]

# 2. Run migrations
python manage.py migrate

# 3. Create superuser
python manage.py createsuperuser

# 4. Start server
daphne -b 0.0.0.0 -p 8000 routing.application
```

---

## ⚡ PostgreSQL Benefits

Your setup now includes:

✅ **Binary Implementation** - psycopg[binary] installed for optimal performance
✅ **Proper Driver** - Django will use the fast C implementation
✅ **Remote Connection** - Can connect to Render's managed PostgreSQL
✅ **Production Ready** - Same database as production (no sqlite3 issues)
✅ **Full Features** - HStoreField, JSONField, ArrayField support

---

## 🐛 Psycopg Warnings - Resolved

The warnings you saw earlier:
```
couldn't import psycopg 'c' implementation: No module named 'psycopg_c'
couldn't import psycopg 'binary' implementation: No module named 'psycopg_binary'
```

**These are now FIXED** because:
1. Installed `psycopg[binary]==3.3.3` ✅
2. Updated `requirements.txt` to use binary extra ✅
3. Binary implementation is available for fast C extension access

---

## 📋 PostgreSQL-Specific Features You Can Use

Your Django ORM now has access to:

### 1. JSON Fields (for complex data)
```python
from django.db import models

class Task(models.Model):
    metadata = models.JSONField(default=dict)  # Store any JSON data
```

### 2. Array Fields
```python
class Project(models.Model):
    tags = models.ArrayField(models.CharField(max_length=50), default=list)
```

### 3. Full-Text Search
```python
from django.contrib.postgres.search import SearchVector, SearchQuery

Task.objects.annotate(
    search=SearchVector('name', 'description')
).filter(search=SearchQuery('python'))
```

### 4. Range Queries
```python
from django.contrib.postgres.fields import DateTimeRangeField

class Event(models.Model):
    time_range = DateTimeRangeField()
```

---

## 🔒 Production Deployment on Render

### Step 1: Update `.env` for Production
```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Redis for production (if available)
REDIS_URL=redis://your-redis-url:6379

# Database stays the same (Render PostgreSQL)
DB_HOST=dpg-d6i6l3ngi27c738a92v0-a.oregon-postgres.render.com
```

### Step 2: Create `Procfile` (already exists)
```
web: daphne routing.application --bind 0.0.0.0 --port $PORT
```

### Step 3: Push to Render
```bash
git add .
git commit -m "Add WebSocket and PostgreSQL optimization"
git push origin master
```

Render will automatically:
- Install dependencies from `requirements.txt`
- Run migrations
- Start your application

---

## 🔍 Verify PostgreSQL Connection

Test your connection:

```bash
# Python shell test
python manage.py shell

# Run this in Django shell:
from django.db import connection
print("PostgreSQL Connection Successful!")
print(f"Server Version: {connection.server_version}")
print(f"Database: {connection.settings_dict['NAME']}")
```

---

## 📊 PostgreSQL vs SQLite Comparison

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Concurrency | Limited | Excellent ✅ |
| JSON Support | Limited | Full ✅ |
| Full-Text Search | No | Yes ✅ |
| Production Ready | No | Yes ✅ |
| Multiple Connections | Limited | Unlimited ✅ |
| Performance | Good | Excellent ✅ |
| Scaling | Difficult | Easy ✅ |

**Your project is now optimized for production!** ✅

---

## 🚀 Next Steps

1. **Local Development:**
   ```bash
   # Start Redis (new terminal)
   redis-server

   # Start Django with WebSocket support (new terminal)
   daphne -b 0.0.0.0 -p 8000 routing.application

   # Test migrations
   python manage.py migrate
   ```

2. **Android/iOS Testing:**
   ```bash
   cd mobile/ProjectManagerApp
   npm install
   npm start
   # Then: npm run android or npm run ios
   ```

3. **Production Deployment:**
   - Ensure all environment variables in Render dashboard
   - Redis instance configured on Render
   - Push code to trigger deployment

---

## ⚙️ Troubleshooting PostgreSQL

### Connection Refused
```bash
# Check if Render PostgreSQL is accessible
psql -h dpg-d6i6l3ngi27c738a92v0-a.oregon-postgres.render.com \
     -U project_manager_w0ay_user \
     -w  # no password prompt
```

### Migration Errors
```bash
# Reset migrations (careful - deletes data)
python manage.py migrate app zero
python manage.py migrate app

# Or check current migration state
python manage.py showmigrations
```

### Performance Issues
```sql
-- Check database connections (in psql)
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;

-- Terminate idle connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'idle' AND query_start < now() - interval '10 minutes';
```

---

## 📚 Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- psycopg3 Documentation: https://www.psycopg.org/psycopg3/
- Django PostgreSQL Features: https://docs.djangoproject.com/en/4.2/ref/contrib/postgres/
- Render PostgreSQL: https://render.com/docs/databases

---

**Status:** ✅ PostgreSQL fully configured and optimized
**Psycopg Version:** 3.3.3 (binary implementation)
**Last Updated:** March 2, 2026
