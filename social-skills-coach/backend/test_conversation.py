import requests
import json

# API URL
BASE_URL = "http://localhost:8000/api"

def test_register():
    """Test user registration endpoint"""
    endpoint = f"{BASE_URL}/register"
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(endpoint, json=data)
    print(f"\nRegistration Response ({response.status_code}):")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

def test_login():
    """Test user login endpoint"""
    endpoint = f"{BASE_URL}/login"
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(endpoint, json=data)
    print(f"\nLogin Response ({response.status_code}):")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

def test_conversation_anonymous():
    """Test conversation endpoint without authentication"""
    endpoint = f"{BASE_URL}/conversation"
    data = {
        "user_input": "I get nervous when talking to new people at social events. How can I start conversations more easily?"
    }
    
    response = requests.post(endpoint, json=data)
    print(f"\nConversation Response (Anonymous) ({response.status_code}):")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

def test_conversation_authenticated(token):
    """Test conversation endpoint with authentication"""
    endpoint = f"{BASE_URL}/conversation"
    data = {
        "user_input": "How can I improve my active listening skills during conversations?"
    }
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(endpoint, json=data, headers=headers)
    print(f"\nConversation Response (Authenticated) ({response.status_code}):")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

if __name__ == "__main__":
    print("Testing Social Skills Coach API - Conversation Endpoint")
    print("=====================================================")
    
    # Test registration
    try:
        register_result = test_register()
    except Exception as e:
        print(f"Registration failed: {str(e)}")
        register_result = None
    
    # Test login
    try:
        login_result = test_login()
        if login_result.get("success"):
            token = login_result.get("access_token")
        else:
            token = None
    except Exception as e:
        print(f"Login failed: {str(e)}")
        token = None
    
    # Test anonymous conversation
    try:
        test_conversation_anonymous()
    except Exception as e:
        print(f"Anonymous conversation test failed: {str(e)}")
    
    # Test authenticated conversation
    if token:
        try:
            test_conversation_authenticated(token)
        except Exception as e:
            print(f"Authenticated conversation test failed: {str(e)}")
    else:
        print("\nSkipping authenticated conversation test as login failed.") 