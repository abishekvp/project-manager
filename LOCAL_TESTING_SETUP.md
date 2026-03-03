# Local Testing Configuration for Project Manager

## 🔧 Setup Instructions for Local Testing

Since the remote Render database may have IP restrictions, use this for local development.

### Option 1: Local SQLite (Quick Testing)

Create `.env.local` for local testing:
```env
# Django Settings
SECRET_KEY=8-#^k$adqn(p5)%w!ni(q%e*+u=mx%d(6!a1i!+50mu99(vh6+
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# LocalSQLite Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.local.sqlite3

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:19000,http://localhost:19001,http://192.168.1.100:19000

# Security (disabled for local testing)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

Then run:
```bash
# For local testing with SQLite
export DJANGO_SETTINGS_MODULE=main.settings
python manage.py migrate
python manage.py createsuperuser
daphne -b 0.0.0.0 -p 8000 routing.application
```

---

### Option 2: Local PostgreSQL (Recommended for Production Testing)

**Windows Setup:**

1. **Download PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Download PostgreSQL 15 or 16

2. **Install PostgreSQL:**
   - Run installer
   - Remember the password you set
   - Keep default settings (port 5432)

3. **Create Database:**
   ```bash
   # Open Command Prompt or PowerShell
   psql -U postgres

   # In PostgreSQL prompt:
   CREATE DATABASE project_manager_dev;
   \q
   ```

4. **Update `.env` for local PostgreSQL:**
   ```env
   # Django Settings
   SECRET_KEY=8-#^k$adqn(p5)%w!ni(q%e*+u=mx%d(6!a1i!+50mu99(vh6+
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Local PostgreSQL
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=project_manager_dev
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password_here
   DB_HOST=localhost
   DB_PORT=5432

   # Redis Configuration
   REDIS_URL=redis://127.0.0.1:6379

   # CORS Configuration
   CORS_ALLOWED_ORIGINS=http://localhost:19000,http://localhost:19001,http://192.168.1.100:19000

   # Security
   SECURE_SSL_REDIRECT=False
   SESSION_COOKIE_SECURE=False
   CSRF_COOKIE_SECURE=False
   ```

5. **Run Migration & Start Server:**
   ```bash
   # Install dependencies (if not already done)
   pip install -r requirements.txt

   # Create tables
   python manage.py migrate

   # Create admin user
   python manage.py createsuperuser

   # Start Redis in one terminal
   redis-server

   # Start Django server in another terminal
   daphne -b 0.0.0.0 -p 8000 routing.application
   ```

---

## ✅ Verify Everything Works

### 1. Check Django Setup
```bash
python manage.py shell
>>> from django.db import connection
>>> print("Database:", connection.settings_dict['NAME'])
>>> print("Engine:", connection.settings_dict['ENGINE'])
```

### 2. Generate API Documentation
```bash
python manage.py drf_spectacular --file schema.yml
```

### 3. Test WebSocket
```bash
# In another terminal, test WebSocket connection
pip install websocket-client
python -c "
import websocket
try:
    ws = websocket.create_connection('ws://localhost:8000/ws/notifications/')
    print('✅ WebSocket connection successful!')
    ws.close()
except Exception as e:
    print(f'❌ WebSocket connection failed: {e}')
"
```

### 4. Test API Endpoints
```bash
# Get CSRF token
curl -c cookies.txt http://localhost:8000/api/notifications/

# Login
curl -b cookies.txt -X POST http://localhost:8000/signin/ \
  -d "email=user@example.com&password=pass"
```

---

## 🌐 For Production (Render)

Keep using the remote PostgreSQL connection:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=project_manager_w0ay
DB_USER=project_manager_w0ay_user
DB_PASSWORD=ltVcFdkjXvtwKTzXa4Rsct5nFaBiy7rw
DB_HOST=dpg-d6i6l3ngi27c738a92v0-a.oregon-postgres.render.com
DB_PORT=5432
```

**Deploy:** Push to Render and it will automatically:
- Install dependencies
- Run migrations
- Start the server

---

## 🐛 Troubleshooting

### psycopg Test
```bash
python -c "import psycopg; print('✅ psycopg installed:', psycopg.__version__)"
```

### Redis Test
```bash
redis-cli ping
# Should output: PONG
```

### PostgreSQL Test
```bash
psql -h localhost -U postgres -d project_manager_dev -c "SELECT 1"
```

### Django Migrations
```bash
python manage.py showmigrations
python manage.py migrate --plan
```

---

## 📋 Summary

**For Local Development:** Use SQLite or Local PostgreSQL
**For Production:** Use Render PostgreSQL
**For WebSockets:** Redis must be running locally (or configured on Render for production)

All code is ready! Just configure your local database and you're set to go!
