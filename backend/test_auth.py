import requests
import json

BASE_URL = 'http://localhost:5000'

def test_register():
    print("\n=== Testing User Registration ===")
    
    # Test valid registration
    register_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/api/register', json=register_data)
    print(f"Registration (valid): {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test duplicate registration (should fail)
    response = requests.post(f'{BASE_URL}/api/register', json=register_data)
    print(f"\nRegistration (duplicate): {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test missing fields
    incomplete_data = {
        'email': 'incomplete@example.com'
        # Missing password
    }
    response = requests.post(f'{BASE_URL}/api/register', json=incomplete_data)
    print(f"\nRegistration (missing fields): {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_login():
    print("\n=== Testing User Login ===")
    
    # Test valid login
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/api/login', json=login_data)
    print(f"Login (valid): {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Save the access token
    token = None
    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"\nAccess Token: {token[:20]}...")
    
    # Test invalid credentials
    invalid_data = {
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }
    response = requests.post(f'{BASE_URL}/api/login', json=invalid_data)
    print(f"\nLogin (invalid credentials): {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test non-existent user
    nonexistent_data = {
        'email': 'nonexistent@example.com',
        'password': 'password123'
    }
    response = requests.post(f'{BASE_URL}/api/login', json=nonexistent_data)
    print(f"\nLogin (non-existent user): {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    return token

def test_protected_endpoints(token):
    print("\n=== Testing Protected Endpoints ===")
    
    if not token:
        print("No token available. Skipping protected endpoint tests.")
        return
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Test protected practice endpoint
    message_data = {
        'message': 'Hello, I want to improve my public speaking skills.'
    }
    response = requests.post(f'{BASE_URL}/api/practice', json=message_data, headers=headers)
    print(f"Protected Practice Endpoint: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test protected progress endpoint
    response = requests.get(f'{BASE_URL}/api/progress', headers=headers)
    print(f"\nProtected Progress Endpoint: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test without token (should fail)
    response = requests.get(f'{BASE_URL}/api/progress')
    print(f"\nNo Token Access (should fail): {response.status_code}")
    print(response.text)

if __name__ == '__main__':
    try:
        print("=== Testing Social Skills Coach Authentication API ===")
        test_register()
        token = test_login()
        test_protected_endpoints(token)
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running.") 