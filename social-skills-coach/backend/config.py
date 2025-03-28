"""
Configuration settings for the Social Skills Coach application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database settings
DB_USER = os.environ.get('DB_USER', 'neondb_owner')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'npg_3vM7YgNJmWrP')
DB_HOST = os.environ.get('DB_HOST', 'ep-wild-pine-a6z492pc-pooler.us-west-2.aws.neon.tech')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'neondb')

# Database URI - prefer direct DATABASE_URL if available
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # SQLAlchemy requires postgresql:// not postgres://
    if DATABASE_URL.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT Settings
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')  # Change this in production!

# OpenAI API Key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')  # Must be set in .env or as environment variable

# Application Settings
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 8000))

# Performance Settings
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 5))  # Timeout for external API calls (seconds)
CONVERSATION_CACHE_SIZE = int(os.environ.get('CONVERSATION_CACHE_SIZE', 100))  # Max number of cached responses 