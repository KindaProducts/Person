"""
Script to create the PostgreSQL database and tables for the Social Skills Coach application.

Run this script after setting up PostgreSQL and before starting the application 
for the first time to initialize the database schema.
"""

from app import app, db
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import config

def create_database():
    """Create the PostgreSQL database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (config.DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            # Create the database
            print(f"Creating database '{config.DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {config.DB_NAME}")
            print(f"Database '{config.DB_NAME}' created successfully!")
        else:
            print(f"Database '{config.DB_NAME}' already exists!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return False

def create_tables():
    """Create the database tables using SQLAlchemy."""
    try:
        print("Creating tables...")
        with app.app_context():
            db.create_all()
        print("Tables created successfully!")
        return True
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    if create_database():
        create_tables()
    else:
        print("Failed to create database. Tables not created.") 