"""
Django startup initialization.
Ensures required directories exist for logging and media files.
"""

import os
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Create necessary directories
DIRS_TO_CREATE = [
    os.path.join(BASE_DIR, 'logs'),
    os.path.join(BASE_DIR, 'media'),
    os.path.join(BASE_DIR, 'staticfiles'),
]

for directory in DIRS_TO_CREATE:
    Path(directory).mkdir(parents=True, exist_ok=True)

# Setup logging directory if not exists
log_dir = os.path.join(BASE_DIR, 'logs')
Path(log_dir).mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
logger.info(f"Initialized directories: {DIRS_TO_CREATE}")
