# Social Skills Coach API

A Flask-based API for a social skills coaching application that provides conversation practice, feedback, and progress tracking.

## Setup

### Prerequisites
- Python 3.9+
- PostgreSQL database (a Neon database is already configured)

### Installation

1. Clone the repository
```bash
git clone https://github.com/KindaProducts/Person.git
cd Person/social-skills-coach/backend
```

2. Create a virtual environment and activate it
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
The `.env` file contains sensitive information such as database credentials and API keys. Make sure to update:
- `OPENAI_API_KEY` with your OpenAI API key
- `JWT_SECRET_KEY` with a secure random string for production

The database is already configured with Neon PostgreSQL:
```
DATABASE_URL=postgresql://neondb_owner:npg_3vM7YgNJmWrP@ep-wild-pine-a6z492pc-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require
```

5. Initialize the database
```bash
python create_db.py
```

6. Run the application
```bash
flask run --host=0.0.0.0 --port=8000
```

The API will start on `http://localhost:8000`

## Database Information

The application uses [Neon PostgreSQL](https://neon.tech/), a fully managed serverless Postgres service:

- **Database Name**: neondb
- **Host**: ep-wild-pine-a6z492pc-pooler.us-west-2.aws.neon.tech
- **Port**: 5432
- **Connection String**: Already configured in .env file

## API Endpoints

### Authentication

#### Register a new user
- **URL**: `/api/register`
- **Method**: `POST`
- **Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
- **Success Response**: 
```json
{
  "success": true,
  "message": "User registered successfully"
}
```
- **Error Response**: 
```json
{
  "success": false,
  "message": "Email already registered"
}
```

#### Login
- **URL**: `/api/login`
- **Method**: `POST`
- **Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
- **Success Response**: 
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "JWT_TOKEN_HERE",
  "user": {
    "email": "user@example.com",
    "id": 1
  }
}
```
- **Error Response**: 
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

### Conversation Practice

#### Practice conversation with AI coach
- **URL**: `/api/conversation`
- **Method**: `POST`
- **Authentication**: JWT token optional
- **Body**:
```json
{
  "user_input": "I feel nervous before social events"
}
```
- **Success Response**: 
```json
{
  "success": true,
  "response": "It's completely normal to feel nervous. Here are some strategies to help...",
  "feedback": "Try to be more specific about what makes you nervous"
}
```

#### Get conversation history
- **URL**: `/api/practice`
- **Method**: `GET`
- **Authentication**: JWT token required
- **Success Response**: Array of conversation objects

### Feedback

#### Get feedback on communication
- **URL**: `/api/feedback`
- **Method**: `POST`
- **Authentication**: None required
- **Body**:
```json
{
  "user_input": "I am sorry but I think I'm not good at talking to people"
}
```
- **Success Response**: 
```json
{
  "success": true,
  "feedback": "Try to avoid apologizing too much in your conversations. Consider making more definitive statements instead of prefacing with 'I think' to sound more confident.",
  "analysis": {
    "polarity": -0.15,
    "subjectivity": 0.7,
    "word_count": 12,
    "pattern_matches": ["Try to avoid apologizing too much in your conversations."]
  }
}
```

### Progress Tracking

#### Get progress data
- **URL**: `/api/progress`
- **Method**: `GET`
- **Authentication**: JWT token required
- **Success Response**: Progress tracking data

## Performance Features

The API includes several optimizations:

1. **Caching**: Conversation responses are cached using an LRU cache to improve response times
2. **Rate limiting**: Endpoints are protected with rate limiting to prevent abuse
3. **Error handling**: Robust error handling with fallbacks for external service failures
4. **Performance monitoring**: All major functions track execution time

## Testing

To test the API endpoints:

```bash
python test_endpoints.py
```

This script will run tests on all endpoints including cache performance, rate limiting, and concurrent request handling.

## Security

- Passwords are hashed using SHA-256
- API authentication uses JWT tokens
- SSL is required for database connections
- Input validation on all endpoints

## License
This project is licensed under the MIT License. 