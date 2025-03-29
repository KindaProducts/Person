#!/usr/bin/env python3
"""
Script to initialize and set up the database for the Social Skills Coach API.
This will create all necessary tables defined in the app models.
"""

import os
import sys
from datetime import date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config
import sqlalchemy as sa
from sqlalchemy import inspect
import psycopg2

def test_connection():
    """Test the PostgreSQL connection using psycopg2 directly."""
    print("\nTesting database connection...")

    try:
        # Create connection string - use URI without SQLAlchemy specific parts
        if config.DATABASE_URL:
            # Extract connection info from URL - remove ?sslmode=require for raw psycopg2
            conn_parts = config.DATABASE_URL.split('?')[0]
            conn_string = conn_parts
        else:
            conn_string = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
        
        print(f"Connecting to: {conn_string.replace(config.DB_PASSWORD, '********')}")
        
        # Connect to the database
        connection = psycopg2.connect(conn_string)
        cursor = connection.cursor()
        
        # Get database version
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"PostgreSQL version: {db_version[0]}")
        
        # Close connection
        cursor.close()
        connection.close()
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return False

def create_app():
    """Create a minimal Flask app for database operations."""
    print("Creating Flask application...")
    app = Flask(__name__)
    
    # Configure the SQLAlchemy database
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    
    # Initialize the database
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    # Define minimal models here to avoid circular imports
    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        
        # Subscription related fields
        stripe_customer_id = db.Column(db.String(255), nullable=True)
        subscription_id = db.Column(db.String(255), nullable=True)
        subscription_status = db.Column(db.String(50), nullable=True)
        tier = db.Column(db.String(50), default='free')
        scenarios_accessed = db.Column(db.Integer, default=0)
        last_reset = db.Column(db.Date, default=date.today)
    
    class Conversation(db.Model):
        __tablename__ = 'conversations'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        timestamp = db.Column(db.DateTime, nullable=False)
        user_input = db.Column(db.Text, nullable=False)
        ai_response = db.Column(db.Text, nullable=False)
    
    class Feedback(db.Model):
        __tablename__ = 'feedbacks'
        id = db.Column(db.Integer, primary_key=True)
        conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
        feedback_text = db.Column(db.Text, nullable=False)
    
    return app, db, User, Conversation, Feedback

def create_tables(app, db):
    """Create all database tables if they don't exist."""
    print("\nCreating database tables...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("Database tables created successfully!")
            
            # Check if tables were created using inspector
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
            print(f"Total tables created: {len(table_names)}")
            
            if "users" in table_names:
                print("- Users table created successfully")
                # Show columns in users table
                columns = [col['name'] for col in inspector.get_columns('users')]
                print(f"  Columns: {', '.join(columns)}")
            else:
                print("- Warning: Users table not created")
                
            if "conversations" in table_names:
                print("- Conversations table created successfully")
            else:
                print("- Warning: Conversations table not created")
                
            if "feedbacks" in table_names:
                print("- Feedbacks table created successfully")
            else:
                print("- Warning: Feedbacks table not created")
                
            return True
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        return False

def create_test_user(app, db, User):
    """Create a test user if no users exist."""
    with app.app_context():
        try:
            user_count = db.session.query(User).count()
            if user_count == 0:
                print("\nCreating test user...")
                
                # Import passlib for password hashing
                from passlib.hash import sha256_crypt
                
                # Create new user
                test_user = User(
                    email="test@example.com",
                    password_hash=sha256_crypt.hash("password123"),
                    tier='free',
                    scenarios_accessed=0,
                    last_reset=date.today()
                )
                db.session.add(test_user)
                db.session.commit()
                print("Test user created successfully:")
                print("- Email: test@example.com")
                print("- Password: password123")
                print("- Tier: free")
            else:
                print(f"\nSkipping test user creation: {user_count} users already exist")
        except Exception as e:
            print(f"Error creating test user: {str(e)}")

if __name__ == "__main__":
    print("=================================================")
    print("SOCIAL SKILLS COACH DATABASE INITIALIZATION")
    print("=================================================")
    print(f"Database URL: {config.SQLALCHEMY_DATABASE_URI.replace(config.DB_PASSWORD, '********')}")
    
    # First test direct connection
    if test_connection():
        # Create Flask app and DB 
        app, db, User, Conversation, Feedback = create_app()
        
        if create_tables(app, db):
            create_test_user(app, db, User)
            print("\nDatabase initialization complete!")
        else:
            print("\nDatabase initialization failed at table creation.")
            sys.exit(1)
    else:
        print("\nDatabase initialization failed at connection test.")
        sys.exit(1)
        
    print("=================================================") 