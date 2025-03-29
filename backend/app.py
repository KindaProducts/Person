from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import sha256_crypt
from datetime import timedelta
import uuid
import openai

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this in production!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

# OpenAI Configuration
openai.api_key = 'your-api-key'  # Replace with your actual API key

# Initialize Flask-RESTful API
api = Api(app)

# User model
class User:
    def __init__(self, email, password):
        self.id = str(uuid.uuid4())
        self.email = email
        # Hash the password before storing
        self.password_hash = sha256_crypt.hash(password)
    
    def verify_password(self, password):
        return sha256_crypt.verify(password, self.password_hash)

# Mock data for demonstration
users_db = {}  # Store users by email
conversations = []
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

# OpenAI Conversation Resource
class Conversation(Resource):
    @jwt_required(optional=True)
    def post(self):
        data = request.get_json()
        
        if not data or 'user_input' not in data:
            return {"success": False, "message": "User input is required"}, 400
        
        user_input = data.get('user_input')
        
        try:
            # Use OpenAI to generate a response
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"You are a social skills coach. Respond to this user input: {user_input}",
                max_tokens=100,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract the AI-generated text
            ai_text = response.choices[0].text.strip()
            
            # Get the current user if authenticated
            current_user = get_jwt_identity()
            
            # Generate some feedback based on the user input
            feedback = None
            if len(user_input.split()) < 5:
                feedback = "Try to be more detailed in your responses."
            elif '?' not in user_input:
                feedback = "Consider asking questions to engage the other person."
            else:
                feedback = "Good job with your communication!"
                
            # Store conversation in history if user is authenticated
            if current_user:
                conversation = {
                    'user_email': current_user,
                    'user_message': user_input,
                    'ai_response': ai_text,
                    'feedback': feedback,
                    'timestamp': 'Just now'  # In a real app, use actual timestamps
                }
                conversations.append(conversation)
            
            return {
                "success": True,
                "response": ai_text,
                "feedback": feedback
            }, 200
            
        except Exception as e:
            return {"success": False, "message": f"Error generating response: {str(e)}"}, 500

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
        if email in users_db:
            return {"success": False, "message": "Email already registered"}, 400
        
        # Create new user and add to database
        new_user = User(email, password)
        users_db[email] = new_user
        
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
        if email in users_db and users_db[email].verify_password(password):
            # Generate access token
            access_token = create_access_token(identity=email)
            return {
                "success": True,
                "message": "Login successful",
                "access_token": access_token,
                "user": {"email": email, "id": users_db[email].id}
            }, 200
        
        return {"success": False, "message": "Invalid credentials"}, 401

# Conversation Practice Resource
class ConversationPractice(Resource):
    @jwt_required()
    def post(self):
        # Get the current user from JWT
        current_user = get_jwt_identity()
        
        data = request.get_json()
        user_message = data.get('message')
        
        # In a real app, this would use an AI model to generate responses
        ai_response = "That's great! Can you tell me more about how you would handle this situation?"
        
        # Generate feedback based on the message
        feedback = "Try to speak more confidently and make eye contact. Your response was clear, but could include more specific details."
        
        conversation = {
            'user_email': current_user,
            'user_message': user_message,
            'ai_response': ai_response,
            'feedback': feedback,
            'timestamp': 'Just now'  # In a real app, use actual timestamps
        }
        
        conversations.append(conversation)
        
        return jsonify({
            'response': ai_response,
            'feedback': feedback
        })
    
    @jwt_required()
    def get(self):
        # Get the current user from JWT
        current_user = get_jwt_identity()
        
        # Filter conversations for the current user
        user_conversations = [c for c in conversations if c.get('user_email') == current_user]
        
        # Return conversation history
        return jsonify(user_conversations)

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
api.add_resource(Conversation, '/api/conversation')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 