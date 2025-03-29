#!/usr/bin/env python3
"""
Stripe Service for Social Skills Coach API.

This module handles interactions with the Stripe API for subscription management.
"""

import stripe
import logging
from datetime import datetime, date
from flask import current_app
import config
from app import app, db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = config.STRIPE_API_KEY

# Product and price IDs (to be configured in Stripe dashboard)
STRIPE_PRODUCTS = {
    'basic': {
        'price_id': 'price_basic', 
        'name': 'Basic Plan'
    },
    'premium': {
        'price_id': 'price_premium',
        'name': 'Premium Plan'
    }
}

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

def create_stripe_customer(user):
    """
    Create a Stripe customer for the given user.
    
    Args:
        user: User object
        
    Returns:
        bool: Success status
    """
    if not user.email:
        logger.error("Cannot create Stripe customer: User has no email")
        return False
    
    # Skip if user already has a Stripe customer ID
    if user.stripe_customer_id:
        logger.info(f"User {user.id} already has Stripe customer: {user.stripe_customer_id}")
        return True
    
    try:
        # Create a new Stripe customer
        customer = stripe.Customer.create(
            email=user.email,
            metadata={
                'user_id': str(user.id)
            }
        )
        
        # Update user with Stripe customer ID
        user.stripe_customer_id = customer.id
        db.session.commit()
        
        logger.info(f"Created Stripe customer for user {user.id}: {customer.id}")
        return True
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating customer: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error creating Stripe customer: {str(e)}")
        return False

def update_user_subscription(event):
    """
    Update user subscription details based on Stripe webhook event.
    
    Args:
        event: Stripe webhook event
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Import User model here to avoid circular imports
        from app import User
        
        # Extract subscription data from the event
        subscription = event.data.object
        customer_id = subscription.customer
        subscription_id = subscription.id
        status = subscription.status
        
        # Find the user by Stripe customer ID
        with app.app_context():
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            
            if not user:
                return False, f"No user found with Stripe customer ID {customer_id}"
            
            # Update subscription details
            user.subscription_id = subscription_id
            user.subscription_status = status
            
            # Determine the subscription tier based on the price
            # This assumes you have configured price IDs in Stripe that match your tiers
            items = subscription.items.data
            if items:
                price_id = items[0].price.id
                
                # Determine tier based on price ID
                if price_id == STRIPE_PRODUCTS['premium']['price_id']:
                    user.tier = 'premium'
                elif price_id == STRIPE_PRODUCTS['basic']['price_id']:
                    user.tier = 'basic'
                else:
                    # Default to free if price doesn't match
                    user.tier = 'free'
            
            # If subscription is canceled, revert to free tier
            if status in ['canceled', 'unpaid', 'past_due']:
                user.tier = 'free'
            
            db.session.commit()
            
            logger.info(f"Updated subscription for user {user.id}: {status}, tier: {user.tier}")
            return True, f"Subscription updated: {status}, tier: {user.tier}"
            
    except Exception as e:
        logger.error(f"Error processing subscription event: {str(e)}")
        return False, f"Error processing subscription event: {str(e)}"

def handle_subscription_created(event):
    """Handle subscription.created event"""
    logger.info("Processing subscription.created event")
    return update_user_subscription(event)

def handle_subscription_updated(event):
    """Handle subscription.updated event"""
    logger.info("Processing subscription.updated event")
    return update_user_subscription(event)

def handle_subscription_deleted(event):
    """Handle subscription.deleted event"""
    logger.info("Processing subscription.deleted event")
    return update_user_subscription(event)

def create_checkout_session(user, tier):
    """
    Create a Stripe checkout session for the specified tier.
    
    Args:
        user: User object
        tier: Subscription tier ('basic' or 'premium')
        
    Returns:
        str: Checkout session URL or None on error
    """
    if tier not in STRIPE_PRODUCTS:
        logger.error(f"Invalid tier: {tier}")
        return None
    
    # Ensure user has a Stripe customer ID
    if not user.stripe_customer_id:
        success = create_stripe_customer(user)
        if not success:
            return None
    
    try:
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRODUCTS[tier]['price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://yourapp.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://yourapp.com/cancel',
            metadata={
                'user_id': str(user.id),
                'tier': tier
            }
        )
        
        return checkout_session.url
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return None

def cancel_subscription(user):
    """
    Cancel a user's subscription in Stripe.
    
    Args:
        user: User object
        
    Returns:
        bool: Success status
    """
    if not user.subscription_id:
        logger.error(f"User {user.id} has no subscription to cancel")
        return False
    
    try:
        # Cancel the subscription at period end (won't charge again)
        stripe.Subscription.modify(
            user.subscription_id,
            cancel_at_period_end=True
        )
        
        # Update local status
        user.subscription_status = 'canceling'
        db.session.commit()
        
        logger.info(f"Subscription {user.subscription_id} for user {user.id} will be canceled at period end")
        return True
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error canceling subscription: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")
        return False

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

def get_user_by_stripe_customer(customer_id):
    """
    Get a user by their Stripe customer ID.
    
    Args:
        customer_id: Stripe customer ID
        
    Returns:
        User object or None
    """
    # Import User model here to avoid circular imports
    from app import User
    
    with app.app_context():
        return User.query.filter_by(stripe_customer_id=customer_id).first() 