#!/usr/bin/env python3
"""
Subscription Manager for Social Skills Coach API.

This utility provides functions to manage user subscriptions,
check scenario limits, and update subscription statuses.
"""

from datetime import date, timedelta
from app import app, db, User
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Subscription tiers and their limits
SUBSCRIPTION_TIERS = {
    'free': {
        'monthly_scenarios': 5,
        'advanced_features': False,
        'feedback_analysis': False,
    },
    'basic': {
        'monthly_scenarios': 20,
        'advanced_features': True,
        'feedback_analysis': False,
    },
    'premium': {
        'monthly_scenarios': float('inf'),  # Unlimited
        'advanced_features': True,
        'feedback_analysis': True,
    }
}

def check_scenario_access(user):
    """
    Check if user can access more scenarios based on their tier and usage.
    
    Args:
        user: User object to check
        
    Returns:
        tuple: (can_access, message)
    """
    # Reset counter if it's a new month
    if user.last_reset is None or user.last_reset.month != date.today().month:
        user.scenarios_accessed = 0
        user.last_reset = date.today()
        db.session.commit()
        logger.info(f"Reset scenario counter for user {user.id} ({user.email})")
    
    # Get tier limits
    tier = user.tier or 'free'
    if tier not in SUBSCRIPTION_TIERS:
        tier = 'free'  # Default to free if invalid tier
    
    tier_limit = SUBSCRIPTION_TIERS[tier]['monthly_scenarios']
    
    # Check if user is within monthly limit
    if tier_limit == float('inf') or user.scenarios_accessed < tier_limit:
        return True, f"Access granted ({user.scenarios_accessed + 1}/{tier_limit if tier_limit != float('inf') else 'unlimited'})"
    else:
        return False, f"Monthly limit reached ({user.scenarios_accessed}/{tier_limit})"

def increment_scenario_count(user):
    """
    Increment the user's scenario count.
    
    Args:
        user: User object to update
    """
    user.scenarios_accessed += 1
    db.session.commit()
    logger.info(f"Incremented scenario count for user {user.id} to {user.scenarios_accessed}")

def upgrade_user_tier(user, new_tier, subscription_id=None):
    """
    Upgrade a user's subscription tier.
    
    Args:
        user: User object to update
        new_tier: New tier ('free', 'basic', or 'premium')
        subscription_id: Stripe subscription ID
        
    Returns:
        bool: Success status
    """
    if new_tier not in SUBSCRIPTION_TIERS:
        logger.error(f"Invalid tier: {new_tier}")
        return False
    
    try:
        user.tier = new_tier
        if subscription_id:
            user.subscription_id = subscription_id
        user.subscription_status = 'active'
        db.session.commit()
        logger.info(f"Upgraded user {user.id} to {new_tier} tier")
        return True
    except Exception as e:
        logger.error(f"Error upgrading user tier: {str(e)}")
        return False

def cancel_subscription(user):
    """
    Cancel a user's subscription, reverting them to free tier.
    
    Args:
        user: User object to update
        
    Returns:
        bool: Success status
    """
    try:
        user.tier = 'free'
        user.subscription_status = 'canceled'
        # Keep subscription_id for records
        db.session.commit()
        logger.info(f"Canceled subscription for user {user.id}")
        return True
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")
        return False

def get_user_by_email(email):
    """
    Get a user by email.
    
    Args:
        email: User email
        
    Returns:
        User object or None
    """
    with app.app_context():
        return User.query.filter_by(email=email).first()

def get_user_by_id(user_id):
    """
    Get a user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User object or None
    """
    with app.app_context():
        return User.query.get(user_id)

def list_all_subscribers():
    """
    List all subscribed users (basic or premium).
    
    Returns:
        list: Subscribed users
    """
    with app.app_context():
        return User.query.filter(User.tier.in_(['basic', 'premium'])).all()

# Example usage
if __name__ == "__main__":
    with app.app_context():
        # List all users
        all_users = User.query.all()
        print(f"Total users: {len(all_users)}")
        
        for user in all_users:
            print(f"\nUser: {user.email} (ID: {user.id})")
            print(f"Tier: {user.tier}")
            print(f"Scenarios accessed: {user.scenarios_accessed}")
            print(f"Last reset: {user.last_reset}")
            
            # Check scenario access
            can_access, message = check_scenario_access(user)
            print(f"Can access scenarios: {can_access} - {message}")
            
            # Show tier benefits
            tier = user.tier or 'free'
            if tier in SUBSCRIPTION_TIERS:
                benefits = SUBSCRIPTION_TIERS[tier]
                print(f"Tier benefits:")
                for key, value in benefits.items():
                    print(f"  - {key}: {value}")
            else:
                print(f"Invalid tier: {tier}") 