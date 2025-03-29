from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import sha256_crypt
from datetime import timedelta, datetime, date
import uuid
from openai import OpenAI
from textblob import TextBlob
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config
import functools
import time
import logging
import re
from threading import Lock
from collections import OrderedDict
import stripe
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load configuration from config.py
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# OpenAI Configuration
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Stripe Configuration
stripe.api_key = config.STRIPE_API_KEY

# Conversation categories and tier requirements
CATEGORIES = {
    'small_talk': 'free',
    'introductions': 'free',
    'networking': 'basic',
    'conflict_resolution': 'basic',
    'job_interviews': 'premium',
    'dating': 'premium'
}

# Tier order for comparison
TIER_ORDER = {'free': 0, 'basic': 1, 'premium': 2}

# Simple LRU cache for conversation responses
class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = Lock()
    
    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            
            # Move the accessed item to the end to mark it as most recently used
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
    
    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                # Remove the entry and re-insert it at the end
                self.cache.pop(key)
            elif len(self.cache) >= self.capacity:
                # Remove the least recently used item (first item in the OrderedDict)
                self.cache.popitem(last=False)
                
            self.cache[key] = value

# Initialize the conversation cache
conversation_cache = LRUCache(config.CONVERSATION_CACHE_SIZE)

# Rate limiting decorator
def rate_limit(max_calls=5, period=60):
    """Limit the number of calls to a function for each user."""
    def decorator(func):
        # Track calls: {user_id: [(timestamp, count), ...]}
        calls = {}
        lock = Lock()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            user_id = current_user if current_user else request.remote_addr
            
            with lock:
                # Clean up old calls
                now = time.time()
                if user_id in calls:
                    calls[user_id] = [c for c in calls[user_id] if now - c[0] < period]
                    
                    # Check rate limit
                    total_calls = sum(c[1] for c in calls[user_id])
                    if total_calls >= max_calls:
                        return {
                            "success": False, 
                            "message": "Rate limit exceeded. Please try again later."
                        }, 429
                    
                    # Update call count
                    calls[user_id].append((now, 1))
                else:
                    calls[user_id] = [(now, 1)]
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Performance monitoring decorator
def measure_performance(func):
    """Measure and log the execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    return wrapper

# Initialize Flask-RESTful API
api = Api(app)

# Database Models
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
    
    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, password):
        self.email = email
        self.password_hash = sha256_crypt.hash(password)
        self.tier = 'free'
        self.scenarios_accessed = 0
        self.last_reset = date.today()
    
    def verify_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_input = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    
    # Relationships
    feedbacks = db.relationship('Feedback', backref='conversation', lazy=True, cascade='all, delete-orphan')

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=True)  # Store feedback score for analytics

# Import stripe_service after initializing app, db, and models
import stripe_service

# Placeholder responses for conversation simulation
MOCK_RESPONSES = {
    "greeting": "Hello! I'm your social skills coach. What would you like to work on today?",
    "nervousness": "It's completely normal to feel nervous in social situations. Start small by preparing a few conversation starters, focusing on open-ended questions about the event or shared interests. Remember that most people enjoy talking about themselves, so showing genuine interest can make conversations flow more naturally.",
    "listening": "To improve active listening, try the RASA technique: Receive the information without interrupting, Appreciate what's being said with nodding or small verbal cues, Summarize their main points to confirm understanding, and Ask follow-up questions that show you were truly listening.",
    "default": "That's an interesting point. Could you tell me more about how this affects your social interactions? I'm here to help you develop strategies that work for your specific situation."
}

# Fallback response when API fails
FALLBACK_RESPONSE = "I'm currently experiencing high demand. Please try again in a moment. In the meantime, remember that good conversation skills involve active listening, asking open-ended questions, and showing genuine interest in the other person."

# Mock data for demonstration (will be replaced by database)
conversations_temp = []  # Temporary storage for conversations
progress_data = {
    'conversation_count': [5, 8, 12, 10],
    'week_labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    'skill_scores': [
        {'skill': 'Conversation Flow', 'score': 78},
        {'skill': 'Active Listening', 'score': 65},
        {'skill': 'Empathy', 'score': 82},
        {'skill': 'Clarity', 'score': 70}
    ]
}

# Basic route to check if API is running
@app.route('/')
def home():
    return 'Social Skills Coach API Running'

# Stripe webhook route
@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    # Get the webhook request payload
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, config.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle the event based on its type
        event_type = event['type']
        logger.info(f"Received Stripe event: {event_type}")
        
        if event_type == 'customer.subscription.created':
            success, message = stripe_service.handle_subscription_created(event)
        elif event_type == 'customer.subscription.updated':
            success, message = stripe_service.handle_subscription_updated(event)
        elif event_type == 'customer.subscription.deleted':
            success, message = stripe_service.handle_subscription_deleted(event)
        else:
            # Log but ignore other event types
            logger.info(f"Ignoring event type: {event_type}")
            return jsonify({"status": "ignored", "message": f"Event type {event_type} ignored"}), 200
        
        # Return response based on handler result
        if success:
            return jsonify({"status": "success", "message": message}), 200
        else:
            logger.error(f"Error handling {event_type}: {message}")
            return jsonify({"status": "error", "message": message}), 400
            
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid Stripe webhook payload: {str(e)}")
        return jsonify({"status": "error", "message": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid Stripe signature: {str(e)}")
        return jsonify({"status": "error", "message": "Invalid signature"}), 400
    except Exception as e:
        # Any other exceptions
        logger.error(f"Error handling Stripe webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Keyword patterns for feedback enhancement
FEEDBACK_PATTERNS = [
    (r'\b(sorry|apologize|apologies)\b', "Try to avoid apologizing too much in your conversations. It can diminish your message."),
    (r'\b(um|uh|like|you know)\b', "Try to reduce filler words to sound more confident and articulate."),
    (r'\bi think\b', "Consider making more definitive statements instead of prefacing with 'I think' to sound more confident."),
    (r'\b(cant|cannot|can\'t|won\'t|wont)\b', "Focus on what you can do rather than what you can't to maintain a positive tone."),
    (r'\b(never|always)\b', "Avoid absolute terms like 'never' and 'always' as they can sound exaggerated or confrontational."),
    (r'\b(maybe|perhaps|possibly)\b', "Too many qualifiers can make you sound uncertain. Be more direct when appropriate.")
]

# Feedback Resource with enhanced logic
class FeedbackResource(Resource):
    @measure_performance
    def post(self):
        data = request.get_json()
        
        if not data or 'user_input' not in data:
            return {"success": False, "message": "User input is required"}, 400
        
        user_input = data.get('user_input')
        
        # Check if the user is authenticated
        current_user_email = get_jwt_identity()
        if current_user_email:
            user = User.query.filter_by(email=current_user_email).first()
            user_tier = user.tier if user else 'free'
        else:
            user_tier = 'free'
        
        # For free users, return a static message
        if user_tier == 'free':
            return {
                "success": True,
                "feedback": "Good job! Keep practicing.",
                "analysis": {
                    "word_count": len(user_input.split()),
                    "tier_limited": True
                }
            }, 200
        
        # For paid users, provide detailed feedback
        # Use TextBlob to analyze sentiment
        blob = TextBlob(user_input)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Check for patterns in the text
        pattern_feedbacks = []
        for pattern, feedback in FEEDBACK_PATTERNS:
            if re.search(pattern, user_input.lower()):
                pattern_feedbacks.append(feedback)
        
        # Generate feedback based on combined rules
        feedback_text = ""
        if polarity < -0.2:
            feedback_text = "Try to sound more positive in your responses."
        elif polarity > 0.6:
            feedback_text = "Your positivity is great, just make sure to remain authentic."
        elif len(user_input.split()) < 5:
            feedback_text = "Try to elaborate more to create engaging conversations."
        elif subjectivity > 0.8:
            feedback_text = "Consider balancing subjective opinions with objective facts."
        elif '?' not in user_input and len(user_input.split()) > 20:
            feedback_text = "Try including questions to engage the other person."
        else:
            feedback_text = "Good response! Your communication is balanced and effective."
        
        # Add pattern-based feedback if found
        if pattern_feedbacks:
            feedback_text += " " + pattern_feedbacks[0]  # Add the first matched pattern feedback
        
        # Calculate a feedback score (0-100) based on various factors
        score = 50  # Base score
        
        # Adjust based on sentiment
        if -0.1 <= polarity <= 0.5:  # Neutral to slightly positive is good
            score += 10
        elif polarity > 0.5:  # Too positive might be inauthentic
            score += 5
        elif polarity < -0.2:  # Too negative is not good
            score -= 10
            
        # Adjust based on word count (neither too short nor too long)
        word_count = len(user_input.split())
        if 10 <= word_count <= 30:
            score += 10
        elif word_count < 5:
            score -= 10
            
        # Adjust based on questions (engagement)
        if '?' in user_input:
            score += 10
            
        # Adjust based on pattern matches (poor communication habits)
        score -= len(pattern_feedbacks) * 5
        
        # Ensure score is within 0-100 range
        score = max(0, min(100, score))
        
        # Save the feedback score if user is authenticated
        if current_user_email and 'conversation_id' in data:
            try:
                conversation_id = data.get('conversation_id')
                feedback_record = Feedback.query.filter_by(conversation_id=conversation_id).first()
                if feedback_record:
                    feedback_record.score = score
                    db.session.commit()
                    logger.info(f"Updated feedback score for conversation {conversation_id}")
            except Exception as e:
                logger.error(f"Error saving feedback score: {str(e)}")
        
        return {
            "success": True,
            "feedback": feedback_text,
            "analysis": {
                "polarity": polarity,
                "subjectivity": subjectivity,
                "word_count": word_count,
                "pattern_matches": pattern_feedbacks,
                "score": score
            }
        }, 200

# OpenAI Conversation Resource with optimizations
class ConversationResource(Resource):
    @jwt_required(optional=True)
    @measure_performance
    @rate_limit(max_calls=10, period=60)  # Limit to 10 calls per minute
    def post(self):
        data = request.get_json()
        
        if not data or 'user_input' not in data:
            return {"success": False, "message": "User input is required"}, 400
        
        user_input = data.get('user_input')
        category = data.get('category', 'small_talk')  # Default to small_talk if not specified
        
        # Validate the category
        if category not in CATEGORIES:
            return {
                "success": False,
                "message": f"Invalid category. Available categories: {', '.join(CATEGORIES.keys())}"
            }, 400
        
        # Get the current user if authenticated
        current_user_email = get_jwt_identity()
        user = None
        
        if current_user_email:
            user = User.query.filter_by(email=current_user_email).first()
            
            if user:
                # Get user tier and required tier for the category
                user_tier = user.tier or 'free'
                required_tier = CATEGORIES[category]
                
                # Check if user has access to this category based on their tier
                if TIER_ORDER[user_tier] < TIER_ORDER[required_tier]:
                    return {
                        "success": False,
                        "message": f"Upgrade to {required_tier} tier to access the {category} category",
                        "upgrade_needed": True,
                        "required_tier": required_tier
                    }, 403
                
                # For free users, check monthly usage limits
                if user_tier == 'free':
                    today = date.today()
                    
                    # Reset counter if it's a new month
                    if user.last_reset is None or user.last_reset.month != today.month or user.last_reset.year != today.year:
                        user.scenarios_accessed = 0
                        user.last_reset = today
                        db.session.commit()
                        logger.info(f"Reset scenario counter for user {user.id} ({user.email})")
                    
                    # Check if user has reached their monthly limit
                    if user.scenarios_accessed >= 5:
                        return {
                            "success": False,
                            "message": "Monthly limit reached. Upgrade for unlimited access.",
                            "upgrade_needed": True,
                            "scenarios_used": user.scenarios_accessed,
                            "scenarios_limit": 5
                        }, 403
                    
                    # Increment usage counter for free users
                    user.scenarios_accessed += 1
                    db.session.commit()
                    logger.info(f"Incremented scenario count for user {user.id} to {user.scenarios_accessed}")
        
        # Generate a cache key that includes the category
        cache_key = hash(f"{category}:{user_input.lower().strip()}")
        cached_response = conversation_cache.get(cache_key)
        if cached_response:
            logger.info("Cache hit for conversation response")
            ai_text, feedback = cached_response
        else:
            logger.info("Cache miss for conversation response")
            try:
                # If OpenAI API key is not provided, use mock responses
                if not config.OPENAI_API_KEY:
                    # Use placeholder responses for testing
                    ai_text = ""
                    user_input_lower = user_input.lower()
                    
                    if "hello" in user_input_lower or "hi" in user_input_lower:
                        ai_text = MOCK_RESPONSES["greeting"]
                    elif "nervous" in user_input_lower or "anxiety" in user_input_lower or "shy" in user_input_lower:
                        ai_text = MOCK_RESPONSES["nervousness"]
                    elif "listen" in user_input_lower or "listening" in user_input_lower:
                        ai_text = MOCK_RESPONSES["listening"]
                    else:
                        ai_text = MOCK_RESPONSES["default"]
                else:
                    # Use OpenAI API with timeout
                    try:
                        # Include the category in the prompt for more contextual responses
                        system_prompt = f"You are a social skills coach providing helpful, encouraging advice for the '{category}' context. Keep responses concise and practical."
                        
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_input}
                            ],
                            max_tokens=150,
                            temperature=0.7,
                            timeout=config.REQUEST_TIMEOUT
                        )
                        
                        # Extract the AI-generated text
                        ai_text = response.choices[0].message.content.strip()
                    except Exception as e:
                        logger.error(f"OpenAI API error: {str(e)}")
                        # Return fallback response
                        ai_text = FALLBACK_RESPONSE
                
                # Generate feedback based on the user input
                feedback = None
                if len(user_input.split()) < 5:
                    feedback = "Try to be more detailed in your responses."
                elif '?' not in user_input:
                    feedback = "Consider asking questions to engage the other person."
                else:
                    feedback = "Good job with your communication!"
                
                # Store in cache
                conversation_cache.put(cache_key, (ai_text, feedback))
                
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                # Return fallback response
                ai_text = FALLBACK_RESPONSE
                feedback = "Try again later for more personalized feedback."
        
        # Store conversation in database if user is authenticated
        if user:
            try:
                # Create new conversation in database with category
                new_conversation = Conversation(
                    user_id=user.id,
                    user_input=user_input,
                    ai_response=ai_text,
                    category=category
                )
                db.session.add(new_conversation)
                
                # Create feedback record
                new_feedback = Feedback(
                    conversation_id=new_conversation.id,
                    feedback_text=feedback
                )
                db.session.add(new_feedback)
                
                db.session.commit()
            
                # For compatibility with old code, also store in temporary list
                conversation = {
                    'user_email': current_user_email,
                    'user_message': user_input,
                    'ai_response': ai_text,
                    'feedback': feedback,
                    'category': category,
                    'timestamp': 'Just now'
                }
                conversations_temp.append(conversation)
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                # Continue without storing in DB if there's an error
                pass
        
        # For free users, include information about usage
        usage_info = {}
        if user and user.tier == 'free':
            usage_info = {
                "scenarios_used": user.scenarios_accessed,
                "scenarios_limit": 5,
                "remaining": 5 - user.scenarios_accessed
            }
        
        return {
            "success": True,
            "response": ai_text,
            "feedback": feedback,
            "category": category,
            "tier_required": CATEGORIES[category],
            **usage_info
        }, 200

# User Registration Resource
class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        
        if not data:
            return {"success": False, "message": "No input data provided"}, 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Validate inputs
        if not email or not password:
            return {"success": False, "message": "Email and password are required"}, 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {"success": False, "message": "Email already registered"}, 400
        
        # Create new user and add to database
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # Create Stripe customer for the user
        stripe_customer_created = stripe_service.create_stripe_customer(new_user)
        if not stripe_customer_created:
            logger.warning(f"Failed to create Stripe customer for user {new_user.id}")
            # Continue anyway, we can create customer later
        
        return {"success": True, "message": "User registered successfully"}, 201

# User Login Resource
class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        
        if not data:
            return {"success": False, "message": "No input data provided"}, 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Validate inputs
        if not email or not password:
            return {"success": False, "message": "Email and password are required"}, 400
        
        # Check if user exists and verify password
        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            # Generate access token
            access_token = create_access_token(identity=email)
            return {
                "success": True,
                "message": "Login successful",
                "access_token": access_token,
                "user": {
                    "email": email, 
                    "id": user.id,
                    "tier": user.tier,
                    "subscription_status": user.subscription_status
                }
            }, 200
        
        return {"success": False, "message": "Invalid credentials"}, 401

# Subscription Resource
class SubscriptionResource(Resource):
    @jwt_required()
    def get(self):
        """Get current user's subscription info"""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return {"success": False, "message": "User not found"}, 404
        
        # Get tier information from subscription_manager
        tier = user.tier or 'free'
        tier_info = stripe_service.SUBSCRIPTION_TIERS.get(tier, stripe_service.SUBSCRIPTION_TIERS['free'])
        
        # Calculate days until reset
        today = date.today()
        if user.last_reset:
            # If it's a new month, the reset date would be today
            if user.last_reset.month != today.month or user.last_reset.year != today.year:
                next_reset = today
            else:
                # Otherwise, the reset will be on the same day next month
                next_month = today.month + 1 if today.month < 12 else 1
                next_year = today.year if today.month < 12 else today.year + 1
                next_reset = date(next_year, next_month, user.last_reset.day)
        else:
            next_reset = today
        
        return {
            "success": True,
            "tier": tier,
            "status": user.subscription_status,
            "scenarios_used": user.scenarios_accessed,
            "scenarios_limit": tier_info['monthly_scenarios'] if tier_info['monthly_scenarios'] != float('inf') else "unlimited",
            "reset_date": next_reset.strftime('%Y-%m-%d'),
            "features": {
                "advanced_features": tier_info['advanced_features'],
                "feedback_analysis": tier_info['feedback_analysis']
            }
        }, 200
        
    @jwt_required()
    def post(self):
        """Create a subscription checkout session"""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return {"success": False, "message": "User not found"}, 404
        
        data = request.get_json()
        if not data or 'tier' not in data:
            return {"success": False, "message": "Tier is required"}, 400
            
        tier = data.get('tier')
        
        # Validate tier
        if tier not in ['basic', 'premium']:
            return {"success": False, "message": "Invalid tier. Choose 'basic' or 'premium'"}, 400
        
        # Create checkout session
        checkout_url = stripe_service.create_checkout_session(user, tier)
        
        if not checkout_url:
            return {"success": False, "message": "Failed to create checkout session"}, 500
            
        return {
            "success": True,
            "checkout_url": checkout_url
        }, 200

# Subscription Cancel Resource
class SubscriptionCancelResource(Resource):
    @jwt_required()
    def post(self):
        """Cancel user's subscription"""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return {"success": False, "message": "User not found"}, 404
            
        if not user.subscription_id:
            return {"success": False, "message": "No active subscription found"}, 400
            
        # Cancel the subscription
        success = stripe_service.cancel_subscription(user)
        
        if not success:
            return {"success": False, "message": "Failed to cancel subscription"}, 500
            
        return {
            "success": True,
            "message": "Subscription canceled successfully"
        }, 200

# Conversation Practice Resource
class ConversationPractice(Resource):
    @jwt_required()
    def post(self):
        # Get the current user from JWT
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return {"success": False, "message": "User not found"}, 404
        
        data = request.get_json()
        user_message = data.get('message')
        
        # In a real app, this would use an AI model to generate responses
        ai_response = "That's great! Can you tell me more about how you would handle this situation?"
        
        # Generate feedback based on the message
        feedback = "Try to speak more confidently and make eye contact. Your response was clear, but could include more specific details."
        
        # Store in database
        new_conversation = Conversation(
            user_id=user.id,
            user_input=user_message,
            ai_response=ai_response
        )
        db.session.add(new_conversation)
        
        new_feedback = Feedback(
            conversation_id=new_conversation.id,
            feedback_text=feedback
        )
        db.session.add(new_feedback)
        db.session.commit()
        
        # For compatibility with old code
        conversation = {
            'user_email': current_user_email,
            'user_message': user_message,
            'ai_response': ai_response,
            'feedback': feedback,
            'timestamp': 'Just now'
        }
        conversations_temp.append(conversation)
        
        return jsonify({
            'response': ai_response,
            'feedback': feedback
        })
    
    @jwt_required()
    def get(self):
        # Get the current user from JWT
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return {"success": False, "message": "User not found"}, 404
        
        # Get conversations from database
        db_conversations = Conversation.query.filter_by(user_id=user.id).all()
        
        # Format results
        results = []
        for convo in db_conversations:
            # Get the feedback for this conversation
            feedback_record = Feedback.query.filter_by(conversation_id=convo.id).first()
            feedback_text = feedback_record.feedback_text if feedback_record else "No feedback available."
            
            results.append({
                'user_email': current_user_email,
                'user_message': convo.user_input,
                'ai_response': convo.ai_response,
                'feedback': feedback_text,
                'timestamp': convo.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Return conversation history
        return jsonify(results)

# Progress Tracking Resource
class ProgressTracking(Resource):
    @jwt_required()
    def get(self):
        # Get the current user from JWT
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return {"success": False, "message": "User not found"}, 404
        
        # Get user's tier
        user_tier = user.tier or 'free'
        
        # Get conversations for this user
        conversations = Conversation.query.filter_by(user_id=user.id).all()
        
        # Basic stats for all users
        total_conversations = len(conversations)
        
        # Base response for free users
        response = {
            "success": True,
            "scenarios_completed": total_conversations,
            "tier": user_tier
        }
        
        # For basic and premium users, add category stats
        if user_tier in ['basic', 'premium']:
            # Calculate category breakdown
            category_stats = {}
            for convo in conversations:
                category = convo.category or 'uncategorized'
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += 1
            
            # Calculate average feedback score
            avg_score = 0
            feedback_count = 0
            
            for convo in conversations:
                feedbacks = Feedback.query.filter_by(conversation_id=convo.id).all()
                for feedback in feedbacks:
                    if feedback.score is not None:
                        avg_score += feedback.score
                        feedback_count += 1
            
            if feedback_count > 0:
                avg_score = round(avg_score / feedback_count, 1)
            
            # Add to response
            response.update({
                "category_stats": category_stats,
                "average_feedback_score": avg_score
            })
        
        # For premium users, include trends over time
        if user_tier == 'premium':
            # Group conversations by week
            weekly_counts = {}
            weekly_scores = {}
            
            for convo in conversations:
                # Convert timestamp to week number (e.g., "2025-W13")
                week_key = convo.timestamp.strftime("%Y-W%V")
                
                if week_key not in weekly_counts:
                    weekly_counts[week_key] = 0
                    weekly_scores[week_key] = {"total": 0, "count": 0}
                
                weekly_counts[week_key] += 1
                
                # Add feedback scores
                feedbacks = Feedback.query.filter_by(conversation_id=convo.id).all()
                for feedback in feedbacks:
                    if feedback.score is not None:
                        weekly_scores[week_key]["total"] += feedback.score
                        weekly_scores[week_key]["count"] += 1
            
            # Calculate weekly averages
            weekly_averages = {}
            for week, data in weekly_scores.items():
                if data["count"] > 0:
                    weekly_averages[week] = round(data["total"] / data["count"], 1)
                else:
                    weekly_averages[week] = 0
            
            # Format data for charting
            trend_data = {
                "labels": sorted(weekly_counts.keys()),
                "conversation_counts": [weekly_counts.get(week, 0) for week in sorted(weekly_counts.keys())],
                "score_averages": [weekly_averages.get(week, 0) for week in sorted(weekly_averages.keys())]
            }
            
            # Add to response
            response.update({
                "trends": trend_data,
                "improvement_areas": get_improvement_areas(conversations)
            })
        
        return jsonify(response)

def get_improvement_areas(conversations):
    """Calculate areas for improvement based on feedback patterns"""
    # Count pattern occurrences in feedback
    pattern_counts = {}
    low_score_categories = {}
    
    for convo in conversations:
        feedbacks = Feedback.query.filter_by(conversation_id=convo.id).all()
        category = convo.category or 'uncategorized'
        
        if category not in low_score_categories:
            low_score_categories[category] = {"total": 0, "count": 0}
        
        for feedback in feedbacks:
            # Count patterns in feedback text
            for pattern, _ in FEEDBACK_PATTERNS:
                pattern_key = pattern.replace(r'\b', '').replace('|', '_').replace('(', '').replace(')', '')
                if re.search(pattern, feedback.feedback_text.lower()):
                    if pattern_key not in pattern_counts:
                        pattern_counts[pattern_key] = 0
                    pattern_counts[pattern_key] += 1
            
            # Track scores by category
            if feedback.score is not None:
                low_score_categories[category]["total"] += feedback.score
                low_score_categories[category]["count"] += 1
    
    # Calculate average scores by category
    category_averages = {}
    for category, data in low_score_categories.items():
        if data["count"] > 0:
            category_averages[category] = round(data["total"] / data["count"], 1)
    
    # Find common patterns and low-scoring categories
    common_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    worst_categories = sorted(category_averages.items(), key=lambda x: x[1])[:2]
    
    return {
        "common_issues": [{"pattern": p[0], "count": p[1]} for p in common_patterns],
        "weakest_categories": [{"category": c[0], "average_score": c[1]} for c in worst_categories]
    }

# Add resources to API
api.add_resource(UserRegister, '/api/register')
api.add_resource(UserLogin, '/api/login')
api.add_resource(ConversationPractice, '/api/practice')
api.add_resource(ProgressTracking, '/api/progress')
api.add_resource(ConversationResource, '/api/conversation')
api.add_resource(FeedbackResource, '/api/feedback')
api.add_resource(SubscriptionResource, '/api/subscription')
api.add_resource(SubscriptionCancelResource, '/api/subscription/cancel')

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
