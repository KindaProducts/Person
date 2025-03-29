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
    
    # Relationships
    feedbacks = db.relationship('Feedback', backref='conversation', lazy=True, cascade='all, delete-orphan')

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)

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
        
        return {
            "success": True,
            "feedback": feedback_text,
            "analysis": {
                "polarity": polarity,
                "subjectivity": subjectivity,
                "word_count": len(user_input.split()),
                "pattern_matches": pattern_feedbacks
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
        
        # Check cache first
        cache_key = hash(user_input.lower().strip())
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
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a social skills coach providing helpful, encouraging advice. Keep responses concise and practical."},
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
                
        # Get the current user if authenticated
        current_user_email = get_jwt_identity()
        
        # Store conversation in database if user is authenticated
        if current_user_email:
            try:
                user = User.query.filter_by(email=current_user_email).first()
                if user:
                    # Create new conversation in database
                    new_conversation = Conversation(
                        user_id=user.id,
                        user_input=user_input,
                        ai_response=ai_text
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
                    'timestamp': 'Just now'
                }
                conversations_temp.append(conversation)
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                # Continue without storing in DB if there's an error
                pass
        
        return {
            "success": True,
            "response": ai_text,
            "feedback": feedback
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
                "user": {"email": email, "id": user.id}
            }, 200
        
        return {"success": False, "message": "Invalid credentials"}, 401

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
        current_user = get_jwt_identity()
        
        # In a real app, you would fetch progress data specific to this user
        return jsonify(progress_data)

# Add resources to API
api.add_resource(UserRegister, '/api/register')
api.add_resource(UserLogin, '/api/login')
api.add_resource(ConversationPractice, '/api/practice')
api.add_resource(ProgressTracking, '/api/progress')
api.add_resource(ConversationResource, '/api/conversation')
api.add_resource(FeedbackResource, '/api/feedback')

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
