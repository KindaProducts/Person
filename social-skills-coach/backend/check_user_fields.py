#!/usr/bin/env python3
"""
Script to check User model fields after migration.
"""

from app import app, db, User
from datetime import date

def check_user_fields():
    """Check User model fields after migration."""
    print("Checking User model fields after migration...")
    
    # Use application context
    with app.app_context():
        # Get all users
        users = User.query.all()
        
        if not users:
            print("No users found in the database.")
            return
        
        print(f"Found {len(users)} users in the database.")
        
        # Check each user
        for user in users:
            print("\nUser Details:")
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Stripe Customer ID: {user.stripe_customer_id}")
            print(f"Subscription ID: {user.subscription_id}")
            print(f"Subscription Status: {user.subscription_status}")
            print(f"Tier: {user.tier}")
            print(f"Scenarios Accessed: {user.scenarios_accessed}")
            print(f"Last Reset: {user.last_reset}")
            
            # Set defaults if fields are None
            if user.tier is None:
                user.tier = 'free'
                print("Setting default tier to 'free'")
                
            if user.scenarios_accessed is None:
                user.scenarios_accessed = 0
                print("Setting default scenarios_accessed to 0")
                
            if user.last_reset is None:
                user.last_reset = date.today()
                print(f"Setting default last_reset to {date.today()}")
        
        # Commit changes
        db.session.commit()
        print("\nChanges committed to database.")

if __name__ == "__main__":
    check_user_fields() 