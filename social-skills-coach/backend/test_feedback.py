import requests
import json

# API URL
BASE_URL = "http://localhost:8000/api"

def test_feedback(user_input):
    """Test feedback endpoint with a given input"""
    endpoint = f"{BASE_URL}/feedback"
    data = {
        "user_input": user_input
    }
    
    response = requests.post(endpoint, json=data)
    print(f"\nFeedback Response for '{user_input}' ({response.status_code}):")
    print(json.dumps(response.json(), indent=2))
    
    return response.json()

if __name__ == "__main__":
    print("Testing Social Skills Coach API - Feedback Endpoint")
    print("=================================================")
    
    # Test with negative sentiment
    try:
        test_feedback("I hate this")
    except Exception as e:
        print(f"Test failed: {str(e)}")
    
    # Test with short input
    try:
        test_feedback("Hello there")
    except Exception as e:
        print(f"Test failed: {str(e)}")
    
    # Test with positive, longer input
    try:
        test_feedback("I love talking to you and this has been very helpful for me")
    except Exception as e:
        print(f"Test failed: {str(e)}") 