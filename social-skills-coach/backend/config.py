"""
Configuration file for the Social Skills Coach API.
Contains all configuration settings loaded from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-key-not-for-production')

# Request timeout configuration (seconds)
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 10))

# Conversation cache size
CONVERSATION_CACHE_SIZE = int(os.environ.get('CONVERSATION_CACHE_SIZE', 100))

# Database Configuration
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'social_skills_db')

# Database URL (if provided directly)
DATABASE_URL = os.environ.get('DATABASE_URL')

# Build SQLAlchemy Database URI
if DATABASE_URL:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Additional SQLAlchemy Settings
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Application Settings
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 8000))

# Stripe Configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET') 