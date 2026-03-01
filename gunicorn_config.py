"""
Gunicorn configuration for production deployment.
This file is loaded by Gunicorn when running with -c gunicorn_config.py
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'project-manager'

# Server mechanics
daemon = False
pidfile = None
umask = 0
group = None
tmp_upload_dir = None

# SSL (handled by Render's reverse proxy)
# Set to False since Render handles SSL termination
ssl_version = None

# Misc
preload_app = False
