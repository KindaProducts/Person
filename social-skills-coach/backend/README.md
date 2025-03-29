# Social Skills Coach API

A Flask-based API for a social skills coaching application that provides conversation practice, feedback, and progress tracking.

## Setup

### Prerequisites
- Python 3.9+
- PostgreSQL database (a Neon database is already configured)
- Stripe account for subscription management

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
- `STRIPE_API_KEY` with your Stripe secret key
- `STRIPE_WEBHOOK_SECRET` with your Stripe webhook signing secret

The database is already configured with Neon PostgreSQL:
```
DATABASE_URL=postgresql://neondb_owner:npg_3vM7YgNJmWrP@ep-wild-pine-a6z492pc-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require
```

5. Initialize the database
```bash
python create_db.py
```

6. Run database migrations
```bash
flask db upgrade
```

7. Run the application
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

## Database Models

### User Model

The User model now includes subscription-related fields:

```python
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
```

### Subscription Tiers

The application supports three subscription tiers:

1. **Free**
   - 5 conversation scenarios per month
   - Basic features only

2. **Basic**
   - 20 conversation scenarios per month
   - Advanced conversational features
   - $4.99/month

3. **Premium**
   - Unlimited conversation scenarios
   - All features including detailed feedback analysis
   - $9.99/month

## Subscription Management

A subscription management utility is provided in `subscription_manager.py`:

```bash
python subscription_manager.py
```

This utility provides functions to:
- Check and enforce monthly scenario limits
- Upgrade users to premium tiers
- Cancel subscriptions
- List subscribers

## Stripe Integration

The application integrates with [Stripe](https://stripe.com/) for payment processing and subscription management.

### Configuration

To configure Stripe for the application:

1. Create a Stripe account and set up your products and prices
2. Configure the product price IDs in `stripe_service.py`:
```python
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
```
3. Set up a webhook endpoint in your Stripe dashboard pointing to `/stripe-webhook`
4. Update your .env file with your Stripe API key and webhook secret

### Webhook Events

The application processes the following Stripe webhook events:

- `customer.subscription.created`: When a user subscribes to a plan
- `customer.subscription.updated`: When a subscription is updated (change in plans, etc.)
- `customer.subscription.deleted`: When a subscription is canceled or expires

### Testing Webhooks Locally

For local testing, you can use the Stripe CLI to forward webhook events:

```bash
stripe listen --forward-to http://localhost:8000/stripe-webhook
```

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
    "id": 1,
    "tier": "free",
    "subscription_status": null
  }
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
- **Free Tier Limit Exceeded Response**:
```json
{
  "success": false,
  "message": "Monthly limit reached (5/5)",
  "upgrade_needed": true
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

### Subscription Management

#### Get user subscription info
- **URL**: `/api/subscription`
- **Method**: `GET`
- **Authentication**: JWT token required
- **Success Response**: 
```json
{
  "success": true,
  "tier": "free",
  "status": null,
  "scenarios_used": 3,
  "scenarios_limit": 5,
  "reset_date": "2025-04-28",
  "features": {
    "advanced_features": false,
    "feedback_analysis": false
  }
}
```

#### Upgrade subscription
- **URL**: `/api/subscription`
- **Method**: `POST`
- **Authentication**: JWT token required
- **Body**:
```json
{
  "tier": "premium"
}
```
- **Success Response**: 
```json
{
  "success": true,
  "checkout_url": "https://checkout.stripe.com/..."
}
```

#### Cancel subscription
- **URL**: `/api/subscription/cancel`
- **Method**: `POST`
- **Authentication**: JWT token required
- **Success Response**: 
```json
{
  "success": true,
  "message": "Subscription canceled successfully"
}
```

### Stripe Webhooks

#### Webhook endpoint
- **URL**: `/stripe-webhook`
- **Method**: `POST`
- **Authentication**: Stripe signature verification
- **Body**: Stripe webhook event payload
- **Success Response**: 
```json
{
  "status": "success",
  "message": "Subscription updated: active, tier: premium"
}
```

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

## Database Migrations

The application uses Flask-Migrate for database migrations:

1. Generate a migration:
```bash
flask db migrate -m "description of changes"
```

2. Apply migrations:
```bash
flask db upgrade
```

3. Rollback a migration:
```bash
flask db downgrade
```

## Security

- Passwords are hashed using SHA-256
- API authentication uses JWT tokens
- SSL is required for database connections
- Input validation on all endpoints
- Stripe webhook signatures are verified

## License
This project is licensed under the MIT License. 