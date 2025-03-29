import requests
import json

BASE_URL = 'http://localhost:5000'

def test_home():
    response = requests.get(f'{BASE_URL}/')
    print(f"Home endpoint: {response.status_code} - {response.text}")

def test_auth():
    # Test registration
    register_data = {
        'action': 'register',
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/api/auth', json=register_data)
    print(f"Registration: {response.status_code} - {json.dumps(response.json(), indent=2)}")
    
    # Test login with correct credentials
    login_data = {
        'action': 'login',
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/api/auth', json=login_data)
    print(f"Login (correct): {response.status_code} - {json.dumps(response.json(), indent=2)}")
    
    # Test login with incorrect credentials
    wrong_login_data = {
        'action': 'login',
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }
    response = requests.post(f'{BASE_URL}/api/auth', json=wrong_login_data)
    print(f"Login (incorrect): {response.status_code} - {json.dumps(response.json(), indent=2)}")

def test_practice():
    # Test posting a message
    message_data = {
        'message': 'Hello, I\'m trying to improve my public speaking skills.'
    }
    response = requests.post(f'{BASE_URL}/api/practice', json=message_data)
    print(f"Practice (post): {response.status_code} - {json.dumps(response.json(), indent=2)}")
    
    # Test getting conversation history
    response = requests.get(f'{BASE_URL}/api/practice')
    print(f"Practice (get): {response.status_code} - {json.dumps(response.json(), indent=2)}")

def test_progress():
    response = requests.get(f'{BASE_URL}/api/progress')
    print(f"Progress: {response.status_code} - {json.dumps(response.json(), indent=2)}")

if __name__ == '__main__':
    print("=== Testing Social Skills Coach API ===")
    try:
        test_home()
        print("\n")
        test_auth()
        print("\n")
        test_practice()
        print("\n")
        test_progress()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running.") 