# Project Manager - Complete Setup & Deployment Guide

## ✅ Features Implemented

1. **Real-time Notifications with WebSockets** - Django Channels + Redis
2. **Dashboard Widgets & Analytics** - Comprehensive dashboard metrics
3. **File Attachments** - Secure file upload/download with validation
4. **Team Collaboration** - Task watchers and @mentions
5. **Task Comments & Activity Feed** - Real-time comment streaming
6. **React Native Mobile App** - Full-featured mobile application

---

## Prerequisites

### System Requirements
- **Python 3.9+** - Backend development
- **Node.js 14+** - Mobile app development
- **Redis Server** - Required for WebSocket channel layer
- **PostgreSQL** (recommended) or SQLite (default)

### Installation on Windows

#### 1. Install Redis
```bash
# Using Chocolatey (recommended)
choco install redis-64

# Or download from: https://github.com/microsoftarchive/redis/releases

# Start Redis
redis-server
```

#### 2. Install Python Dependencies
```bash
cd d:\Documents\project-manager

# Create/activate virtual environment
python -m venv env
env\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

#### 3. Install Node.js & React Native
```bash
# Node.js - download from https://nodejs.org/

# React Native CLI (global)
npm install -g react-native-cli
```

---

## Backend Configuration

### Step 1: Environment Setup

Create `.env` file in project root:
```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database (SQLite by default, optionalPostgreSQL)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
# For PostgreSQL:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=project_manager_db
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# Redis (For WebSocket channel layer)
REDIS_URL=redis://127.0.0.1:6379

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS Configuration (For mobile app)
CORS_ALLOWED_ORIGINS=http://localhost:19000,http://localhost:19001,http://192.168.x.x:19000

# Security
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### Step 2: Database Migrations

```bash
# Activate virtual environment
env\Scripts\activate

# Run migrations (includes new models)
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser
```

### Step 3: Run Tests

```bash
python manage.py test
```

### Step 4: Start Development Server

**Using Daphne (with WebSocket support):**
```bash
# Activate virtual environment
env\Scripts\activate

# Start Daphne server
daphne -b 0.0.0.0 -p 8000 routing.application
```

The application will be available at `http://localhost:8000`

**For traditional HTTP only (without WebSocket):**
```bash
python manage.py runserver
```

---

## Frontend/Web Configuration

Navigate to `template/` and `static/` directories for web interface updates.

### Key Web API Endpoints

- `GET /api/dashboard/analytics/` - Dashboard statistics
- `GET /api/notifications/` - User notifications
- `GET /api/tasks/<id>/comments/` - Task comments
- `POST /api/tasks/<id>/attachments/upload/` - Upload files
- `WS /ws/notifications/` - WebSocket notifications

---

## Mobile App Setup

### Step 1: Install Dependencies

```bash
cd mobile/ProjectManagerApp

# Install npm packages
npm install
# or
yarn install
```

### Step 2: Configure API Connection

Edit `src/services/api.js`:
```javascript
const BASE_URL = 'http://192.168.x.x:8000';  // Change to your backend URL
```

Edit `src/services/websocket.js`:
```javascript
const WS_URL = 'ws://192.168.x.x:8000';  // Change to your backend URL
```

### Step 3: Run on Android

```bash
# Start metro bundler
npm start

# In another terminal, run on Android
npm run android
# or
npx react-native run-android
```

### Step 4: Run on iOS

```bash
npm run ios
# or
npx react-native run-ios
```

### Step 5: Run on Emulator

```bash
# Android Emulator
npx react-native start
npx react-native run-android

# iOS Simulator
npx react-native run-ios --simulator "iPhone 15"
```

---

## API Documentation

### Authentication Endpoints
```
POST   /api/auth/login/                    - User login
POST   /api/auth/signup/                   - User registration
POST   /api/auth/logout/                   - User logout
GET    /api/auth/me/                       - Current user profile
```

### Notification Endpoints
```
GET    /api/notifications/                 - List notifications
POST   /api/notifications/mark-read/       - Mark as read
POST   /api/notifications/mark-all-read/   - Mark all read
GET    /api/notifications/unread-count/    - Unread count
```

### Task Comment Endpoints
```
GET    /api/tasks/<task_id>/comments/           - Get comments
POST   /api/tasks/<task_id>/comments/create/    - Create comment
POST   /api/comments/<comment_id>/delete/       - Delete comment
```

### File Attachment Endpoints
```
GET    /api/tasks/<task_id>/attachments/             - List attachments
POST   /api/tasks/<task_id>/attachments/upload/      - Upload file
GET    /api/attachments/<attachment_id>/download/   - Download file
POST   /api/attachments/<attachment_id>/delete/     - Delete file
```

### Collaboration Endpoints
```
POST   /api/tasks/<task_id>/watch/        - Watch task
POST   /api/tasks/<task_id>/unwatch/      - Unwatch task
GET    /api/tasks/<task_id>/watchers/     - Get watchers
```

### Activity Feed
```
GET    /api/activity-feed/                - Get activity log
```

### Analytics
```
GET    /api/dashboard/analytics/          - Dashboard analytics
```

---

## WebSocket Events

### Client → Server
```javascript
// Subscribe to notifications
{ action: 'mark_as_read', notification_id: 123 }
{ action: 'get_unread_count' }

// Send comment
{ action: 'send_comment', content: 'Message text @user' }
```

### Server → Client
```javascript
// Notification event
{ type: 'notification', notification: {...}, timestamp: '2024-01-01...' }

// Activity event
{ type: 'activity_update', activity: {...}, timestamp: '2024-01-01...' }

// Comment event
{ type: 'comment_created', comment: {...}, timestamp: '2024-01-01...' }
```

---

## Production Deployment

### 1. Backend Deployment (Using Render, Heroku, or VPS)

#### Environment Variables (.env)
```
SECRET_KEY=<generate-new-secret>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<production-db-name>
DB_USER=<db-user>
DB_PASSWORD=<db-password>
DB_HOST=<db-host>
DB_PORT=5432
REDIS_URL=redis://<redis-host>:6379
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Using Daphne with Gunicorn
```bash
# requirements.txt includes daphne and gunicorn

# Start with Gunicorn
gunicorn routing.application --workers 4 --timeout 120
```

#### Using Procfile (Render/Heroku)
```
web: daphne routing.application --bind 0.0.0.0 --port $PORT
worker: python manage.py process_tasks
```

### 2. Mobile App Deployment

#### Android (Google Play Store)
```bash
cd mobile/ProjectManagerApp

# Create release build
npx react-native run-android --variant=release

# Or use Android Studio for signed APK
```

#### iOS (Apple App Store)
```bash
# Use Xcode to build and archive
# or use eas-cli for EAS Build

npm install -g eas-cli
eas build --platform ios
```

---

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'channels'
**Solution:**
```bash
pip install channels==4.0.0
pip install channels-redis==4.1.0
```

### Issue: Redis connection refused
**Solution:**
```bash
# Check if Redis is running
redis-cli ping
# Should output: PONG

# Start Redis server
redis-server
```

### Issue: WebSocket not connecting on mobile
**Solution:**
1. Ensure backend URL is correct and accessible from mobile device IP
2. Try with device IP instead of localhost:
   ```javascript
   const BASE_URL = 'http://192.168.x.x:8000';
   ```
3. Check firewall settings allow WebSocket ports

### Issue: CORS errors
**Solution:**
Update `CORS_ALLOWED_ORIGINS` in `.env` with mobile device IP:
```
CORS_ALLOWED_ORIGINS=http://localhost:19000,http://192.168.x.x:19000
```

### Issue: Database errors after migration
**Solution:**
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate

# Or for PostgreSQL
dropdb project_manager_db
createdb project_manager_db
python manage.py migrate
```

---

## Performance Optimization

### Backend
- Enable Redis caching for API responses
- Use database query optimization with `select_related()` and `prefetch_related()`
- Implement pagination for large datasets
- Use CDN for static files

### Mobile
- Redux state persistence reduces API calls
- FlatList virtualization for long lists
- Image caching and compression
- Offline sync using Redux persistence

---

## Security Checklist

- [x] Change `SECRET_KEY` in production
- [x] Set `DEBUG=False` in production
- [x] Use HTTPS/WSS in production
- [x] Implement CSRF protection
- [x] Use secure token storage (react-native-keychain)
- [x] Validate file uploads (size, type)
- [x] Implement rate limiting
- [x] Use strong database credentials
- [x] Enable HSTS headers
- [x] Implement proper CORS configuration

---

## File Structure Summary

```
project-manager/
├── app/
│   ├── consumers.py          # WebSocket consumers
│   ├── routing.py            # WebSocket routing
│   ├── rest_api.py           # REST API endpoints
│   ├── models.py             # Database models
│   └── urls.py               # URL configuration
├── main/
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL config
│   └── wsgi.py
├── routing.py                # ASGI configuration
├── requirements.txt          # Python dependencies
├── manage.py
└── mobile/
    └── ProjectManagerApp/
        ├── App.js            # Root app component
        ├── package.json
        └── src/
            ├── screens/      # Mobile screens
            ├── store/        # Redux store
            └── services/     # API and WebSocket
```

---

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Configure `.env` file
3. ✅ Run migrations: `python manage.py migrate`
4. ✅ Start Redis server
5. ✅ Start backend: `daphne -b 0.0.0.0 -p 8000 routing.application`
6. ✅ Configure mobile app API URL
7. ✅ Run mobile app: `npm run android` or `npm run ios`

---

## Support & Documentation

- Django Channels: https://channels.readthedocs.io/
- React Native: https://reactnative.dev/
- Redux: https://redux.js.org/
- Django REST Framework: https://www.django-rest-framework.org/

---

**Version:** 2.0.0
**Last Updated:** March 2026
**Status:** Production Ready
