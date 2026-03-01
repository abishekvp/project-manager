#!/usr/bin/env python
"""
Deployment Verification Script
Verifies that the Django project is properly configured for Render deployment.
Run: python verify_deployment.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_required_files():
    """Check if all required deployment files exist."""
    print("📋 Checking required files...")
    required_files = [
        'Procfile',
        'render.yaml',
        'runtime.txt',
        'requirements.txt',
        '.env.example',
        'gunicorn_config.py',
        'generate_secret_key.py',
        'main/settings.py',
        'main/wsgi.py',
    ]
    
    missing = []
    for file in required_files:
        path = BASE_DIR / file
        if path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0

def check_environment_config():
    """Check if settings.py uses environment variables."""
    print("\n🔧 Checking environment configuration...")
    settings_path = BASE_DIR / 'main' / 'settings.py'
    
    if not settings_path.exists():
        print("  ❌ settings.py not found")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    checks = {
        "Uses 'decouple'": "from decouple import config" in content,
        "SECRET_KEY from env": "config('SECRET_KEY'" in content,
        "DEBUG from env": "config('DEBUG'" in content,
        "ALLOWED_HOSTS from env": "config('ALLOWED_HOSTS'" in content,
        "Database from env": "config('DB_" in content,
        "Security headers": "SECURE_SSL_REDIRECT" in content,
        "Logging configured": "LOGGING = {" in content,
    }
    
    all_ok = True
    for check, result in checks.items():
        if result:
            print(f"  ✅ {check}")
        else:
            print(f"  ❌ {check}")
            all_ok = False
    
    return all_ok

def check_requirements():
    """Check if production dependencies are in requirements.txt."""
    print("\n📦 Checking dependencies...")
    req_path = BASE_DIR / 'requirements.txt'
    
    if not req_path.exists():
        print("  ❌ requirements.txt not found")
        return False
    
    with open(req_path, 'r') as f:
        content = f.read()
    
    required_packages = {
        'Django': 'Django' in content,
        'psycopg': 'psycopg' in content,
        'python-decouple': 'decouple' in content,
        'gunicorn': 'gunicorn' in content,
        'whitenoise': 'whitenoise' in content,
    }
    
    all_ok = True
    for package, present in required_packages.items():
        if present:
            print(f"  ✅ {package}")
        else:
            print(f"  ❌ {package} - MISSING")
            all_ok = False
    
    return all_ok

def check_security():
    """Check security configurations."""
    print("\n🔒 Checking security configuration...")
    settings_path = BASE_DIR / 'main' / 'settings.py'
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    security_checks = {
        "SECURE_SSL_REDIRECT": "SECURE_SSL_REDIRECT = True" in content,
        "SESSION_COOKIE_SECURE": "SESSION_COOKIE_SECURE = True" in content,
        "CSRF_COOKIE_SECURE": "CSRF_COOKIE_SECURE = True" in content,
        "SECURE_BROWSER_XSS_FILTER": "SECURE_BROWSER_XSS_FILTER = True" in content,
        "X_FRAME_OPTIONS": "X_FRAME_OPTIONS = 'DENY'" in content,
        "HSTS configured": "SECURE_HSTS_SECONDS" in content,
    }
    
    all_ok = True
    for check, result in security_checks.items():
        if result:
            print(f"  ✅ {check}")
        else:
            print(f"  ⚠️  {check} - Not configured")
            all_ok = False
    
    return all_ok

def check_documentation():
    """Check if documentation files exist."""
    print("\n📚 Checking documentation...")
    docs = [
        'README.md',
        'DEPLOYMENT.md',
        'QUICKSTART.md',
        'DEPLOYMENT_CHECKLIST.md',
        'ENV_VARIABLES.md',
        'QUICK_REFERENCE.md',
    ]
    
    missing = []
    for doc in docs:
        path = BASE_DIR / doc
        if path.exists():
            print(f"  ✅ {doc}")
        else:
            print(f"  ⚠️  {doc} - Missing")
            missing.append(doc)
    
    return len(missing) == 0

def check_gitignore():
    """Check if .gitignore has production files."""
    print("\n🚫 Checking .gitignore...")
    gitignore_path = BASE_DIR / '.gitignore'
    
    if not gitignore_path.exists():
        print("  ⚠️  .gitignore not found")
        return False
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    checks = {
        ".env files ignored": ".env" in content,
        "venv ignored": "venv" in content,
        "__pycache__ ignored": "__pycache__" in content,
        "*.log ignored": "*.log" in content,
        "db.sqlite3 ignored": "sqlite3" in content,
        "staticfiles ignored": "staticfiles" in content,
    }
    
    all_ok = True
    for check, result in checks.items():
        if result:
            print(f"  ✅ {check}")
        else:
            print(f"  ⚠️  {check}")
            all_ok = False
    
    return all_ok

def check_django_setup():
    """Check Django specific configurations."""
    print("\n🎯 Checking Django setup...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        
        # Try importing settings to check for syntax errors
        from main import settings
        
        checks = {
            "ALLOWED_HOSTS set": bool(settings.ALLOWED_HOSTS),
            "DATABASES configured": bool(settings.DATABASES),
            "STATIC_ROOT set": bool(settings.STATIC_ROOT),
            "WSGI configured": settings.WSGI_APPLICATION is not None,
        }
        
        all_ok = True
        for check, result in checks.items():
            if result:
                print(f"  ✅ {check}")
            else:
                print(f"  ❌ {check}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"  ❌ Error importing settings: {e}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("🚀 Render Deployment Verification Script")
    print("=" * 60)
    
    results = {
        "Required Files": check_required_files(),
        "Environment Configuration": check_environment_config(),
        "Dependencies": check_requirements(),
        "Security": check_security(),
        "Documentation": check_documentation(),
        ".gitignore": check_gitignore(),
        "Django Setup": check_django_setup(),
    }
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION RESULTS")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "⚠️  INCOMPLETE"
        print(f"{check:<30} {status}")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Your project is ready for Render deployment!")
        print("\nNext steps:")
        print("1. Review DEPLOYMENT.md")
        print("2. Generate SECRET_KEY: python generate_secret_key.py")
        print("3. Create PostgreSQL database on Render")
        print("4. Create Web Service on Render")
        print("5. Configure environment variables")
        print("6. Deploy!")
        return 0
    else:
        print("\n⚠️  Some checks need attention.")
        print("Review the items marked with ⚠️ or ❌ above.")
        print("See DEPLOYMENT.md for more information.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
