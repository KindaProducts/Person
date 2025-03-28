"""
Script to check users in the database.
"""

from app import app, db, User

def list_users():
    """List all users in the database."""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in the database.")
            return
        
        print(f"Found {len(users)} user(s) in the database:")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}")

if __name__ == "__main__":
    list_users() 