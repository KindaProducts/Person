# Social Skills Coach API

This is the backend API for the Social Skills Coach application, which helps users improve their social skills through AI-powered conversation practice and feedback.

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

The API will start at `http://localhost:8000`.

## API Endpoints

### Authentication

#### Register a new user

- **URL**: `/api/register`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**:
    ```json
    {
      "success": true,
      "message": "User registered successfully"
    }
    ```
- **Error Response**:
  - **Code**: 400
  - **Content**:
    ```json
    {
      "success": false,
      "message": "Email already registered"
    }
    ```

#### User Login

- **URL**: `/api/login`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "success": true,
      "message": "Login successful",
      "access_token": "jwt-token-here",
      "user": {
        "email": "user@example.com",
        "id": "user-id-here"
      }
    }
    ```
- **Error Response**:
  - **Code**: 401
  - **Content**:
    ```json
    {
      "success": false,
      "message": "Invalid credentials"
    }
    ```

### AI Conversation

#### Get AI response to a user message

- **URL**: `/api/conversation`
- **Method**: `POST`
- **Authentication**: Optional (JWT Token)
- **Body**:
  ```json
  {
    "user_input": "I get nervous when talking to new people at social events. How can I start conversations more easily?"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "success": true,
      "response": "Starting conversations can be challenging! Try preparing a few open-ended questions beforehand, like asking about the event, current news, or shared interests. Remember that most people enjoy talking about themselves, so showing genuine interest can help break the ice. Also, positioning yourself near the food or drink area can give you natural conversation starters.",
      "feedback": "Good job with your communication!"
    }
    ```
- **Error Response**:
  - **Code**: 400
  - **Content**:
    ```json
    {
      "success": false,
      "message": "User input is required"
    }
    ```
  - **Code**: 500
  - **Content**:
    ```json
    {
      "success": false,
      "message": "Error generating response: API error"
    }
    ```
- **Notes**:
  - If used with authentication, the conversation will be stored in the user's history
  - Without authentication, the response is generated but not stored

### Conversation Practice

#### Start or continue a practice conversation

- **URL**: `/api/practice`
- **Method**: `POST`
- **Authentication**: Required (JWT Token)
- **Body**:
  ```json
  {
    "message": "Hello, I'm practicing my social skills."
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "response": "That's great! Can you tell me more about how you would handle this situation?",
      "feedback": "Try to speak more confidently and make eye contact. Your response was clear, but could include more specific details."
    }
    ```

#### Get conversation history

- **URL**: `/api/practice`
- **Method**: `GET`
- **Authentication**: Required (JWT Token)
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    [
      {
        "user_email": "user@example.com",
        "user_message": "Hello, I'm practicing my social skills.",
        "ai_response": "That's great! Can you tell me more about how you would handle this situation?",
        "feedback": "Try to speak more confidently and make eye contact. Your response was clear, but could include more specific details.",
        "timestamp": "Just now"
      }
    ]
    ```

### Progress Tracking

#### Get progress data

- **URL**: `/api/progress`
- **Method**: `GET`
- **Authentication**: Required (JWT Token)
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "conversation_count": [5, 8, 12, 10],
      "week_labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
      "skill_scores": [
        {"skill": "Conversation Flow", "score": 78},
        {"skill": "Active Listening", "score": 65},
        {"skill": "Empathy", "score": 82},
        {"skill": "Clarity", "score": 70}
      ]
    }
    ```

## Testing the API

### Using Postman

1. **Register a new user**:
   - Create a POST request to `http://localhost:8000/api/register`
   - Set body to raw JSON with email and password
   - Send the request

2. **Login**:
   - Create a POST request to `http://localhost:8000/api/login`
   - Set body to raw JSON with email and password
   - Send the request and copy the access_token from the response

3. **Test the Conversation Endpoint**:
   - Create a POST request to `http://localhost:8000/api/conversation`
   - Set body to raw JSON with a user_input field
   - For authenticated requests:
     - Add an Authorization header with value `Bearer {your-token}`
   - Send the request

4. **Test protected endpoints**:
   - Add Authorization header with value `Bearer {your-token}` to all requests
   - Create requests to `/api/practice` or `/api/progress` endpoints

### Using curl

1. **Register**:
   ```
   curl -X POST http://localhost:8000/api/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

2. **Login**:
   ```
   curl -X POST http://localhost:8000/api/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

3. **Use the conversation endpoint (anonymous)**:
   ```
   curl -X POST http://localhost:8000/api/conversation \
     -H "Content-Type: application/json" \
     -d '{"user_input":"I get nervous when talking to new people at social events. How can I start conversations more easily?"}'
   ```

4. **Use the conversation endpoint (authenticated)**:
   ```
   curl -X POST http://localhost:8000/api/conversation \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {your-token}" \
     -d '{"user_input":"How can I improve my active listening skills during conversations?"}'
   ```

5. **Use other protected endpoints**:
   ```
   curl -X GET http://localhost:8000/api/practice \
     -H "Authorization: Bearer {your-token}"
   ```

## Using the Test Scripts

The project includes test scripts to help verify the API functionality:

1. **test_auth.py** - Tests user registration and login
2. **test_conversation.py** - Tests the conversation endpoint with and without authentication

Run the tests with:
```
python test_auth.py
python test_conversation.py
```

> Note: Make sure the server is running before executing the test scripts. 