#!/usr/bin/env python3
"""
Test script for the Social Skills Coach API endpoints.
Tests the optimized /conversation and /feedback endpoints
with various inputs to verify functionality.
"""

import requests
import time
import json
import concurrent.futures

# API base URL
BASE_URL = "http://localhost:8000/api"

# Test data
conversation_inputs = [
    "I feel anxious in social situations with new people",
    "How can I be more confident when speaking in groups?",
    "I need advice on how to make small talk at parties",
    "What are good ways to end a conversation politely?",
    "How do I know if I'm talking too much in a conversation?"
]

feedback_inputs = [
    "I am sorry but I am very nervous and maybe I should not be here. I think this is not for me.",
    "I definitely can't do this, it's always so hard for me to talk to people.",
    "Um, like, I kind of want to talk to people but you know I get nervous.",
    "Perhaps I will try to maybe possibly go to the party tonight if I'm not too tired.",
    "This is interesting and I appreciate your help with my social skills."
]

def test_conversation_endpoint():
    """Test the /conversation endpoint with different inputs."""
    print("\n==== Testing /conversation endpoint ====")
    
    for i, user_input in enumerate(conversation_inputs):
        print(f"\nTesting input {i+1}: '{user_input[:30]}...'")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/conversation", 
            json={"user_input": user_input}
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response received in {elapsed:.2f} seconds")
            print(f"AI Response: {data.get('response')[:75]}...")
            print(f"Feedback: {data.get('feedback')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

def test_feedback_endpoint():
    """Test the /feedback endpoint with different inputs."""
    print("\n==== Testing /feedback endpoint ====")
    
    for i, user_input in enumerate(feedback_inputs):
        print(f"\nTesting input {i+1}: '{user_input[:30]}...'")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/feedback", 
            json={"user_input": user_input}
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response received in {elapsed:.2f} seconds")
            print(f"Feedback: {data.get('feedback')}")
            print("Analysis:")
            for key, value in data.get('analysis', {}).items():
                if isinstance(value, list) and len(value) > 0:
                    print(f"- {key}: {value[0][:50]}...")
                else:
                    print(f"- {key}: {value}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

def test_rate_limiting():
    """Test rate limiting by making rapid consecutive requests."""
    print("\n==== Testing rate limiting ====")
    
    start_time = time.time()
    results = []
    
    # Make 15 requests in quick succession to trigger rate limit
    for i in range(15):
        print(f"Making request {i+1}/15...")
        response = requests.post(
            f"{BASE_URL}/conversation", 
            json={"user_input": "Quick request to test rate limiting"}
        )
        results.append({
            "request_num": i+1,
            "status_code": response.status_code,
            "message": response.json().get("message", "") if response.status_code == 429 else "OK"
        })
        
    elapsed = time.time() - start_time
    
    print(f"\nCompleted in {elapsed:.2f} seconds")
    rate_limited = [r for r in results if r["status_code"] == 429]
    
    print(f"Total requests: {len(results)}")
    print(f"Rate limited requests: {len(rate_limited)}")
    
    if rate_limited:
        print("First rate limited response:")
        print(f"Request #{rate_limited[0]['request_num']}: {rate_limited[0]['message']}")

def test_cache_performance():
    """Test cache performance by making repeated identical requests."""
    print("\n==== Testing cache performance ====")
    
    test_input = "How do I start a conversation with someone I just met?"
    
    # First request (cache miss)
    print("\nFirst request (should be cache miss):")
    start_time = time.time()
    response1 = requests.post(
        f"{BASE_URL}/conversation", 
        json={"user_input": test_input}
    )
    elapsed1 = time.time() - start_time
    
    if response1.status_code == 200:
        print(f"Response time: {elapsed1:.4f} seconds")
    
    # Wait a moment
    time.sleep(1)
    
    # Second request with same input (should be cache hit)
    print("\nSecond request with same input (should be cache hit):")
    start_time = time.time()
    response2 = requests.post(
        f"{BASE_URL}/conversation", 
        json={"user_input": test_input}
    )
    elapsed2 = time.time() - start_time
    
    if response2.status_code == 200:
        print(f"Response time: {elapsed2:.4f} seconds")
        
        # Calculate speedup
        if elapsed1 > 0:
            speedup = elapsed1 / elapsed2
            print(f"Speedup factor: {speedup:.2f}x faster")
            
            if speedup > 1.5:
                print("PASS: Cache appears to be working correctly")
            else:
                print("WARNING: Cache might not be working effectively")

def test_concurrent_requests():
    """Test handling multiple concurrent requests."""
    print("\n==== Testing concurrent requests ====")
    
    num_requests = 5
    print(f"Making {num_requests} concurrent requests...")
    
    def make_request(input_text):
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/conversation", 
            json={"user_input": input_text}
        )
        elapsed = time.time() - start_time
        
        return {
            "input": input_text[:20] + "...",
            "status_code": response.status_code,
            "time": elapsed,
            "success": response.status_code == 200
        }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        future_to_input = {
            executor.submit(make_request, input_text): input_text 
            for input_text in conversation_inputs[:num_requests]
        }
        
        results = []
        for future in concurrent.futures.as_completed(future_to_input):
            results.append(future.result())
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\nResults: {len(successful)} successful, {len(failed)} failed")
    print(f"Average response time: {sum(r['time'] for r in results) / len(results):.2f} seconds")
    
    for i, result in enumerate(sorted(results, key=lambda x: x["time"])):
        print(f"{i+1}. Input: {result['input']} - Status: {result['status_code']} - Time: {result['time']:.2f}s")

if __name__ == "__main__":
    print("=================================================")
    print("SOCIAL SKILLS COACH API ENDPOINT TESTING")
    print("=================================================")
    
    # Run the tests
    test_conversation_endpoint()
    test_feedback_endpoint()
    test_cache_performance()
    test_rate_limiting()
    test_concurrent_requests()
    
    print("\n=================================================")
    print("Testing completed")
    print("=================================================") 