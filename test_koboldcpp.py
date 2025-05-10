import sys
import os
import requests
import json

def test_koboldcpp_connection(url="http://localhost:5001/v1", api_key=""):
    """Test connection to Koboldcpp API."""
    print(f"Testing connection to Koboldcpp at {url}...")
    
    # Construct headers
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # Set proper endpoint for models
    models_url = f"{url}/models"
    if models_url.endswith('//models'):
        models_url = models_url.replace('//models', '/models')
    
    # Test getting models
    try:
        response = requests.get(models_url, headers=headers)
        response.raise_for_status()
        
        print("✅ Connection successful!")
        print("\nAvailable models:")
        models = response.json()
        for model in models.get('data', []):
            print(f"  - {model.get('id', 'Unknown')}")
        
        # Test a simple completion
        print("\nTesting chat completion...")
        
        # Set proper endpoint for chat completion
        chat_url = f"{url}/chat/completions"
        if chat_url.endswith('//chat/completions'):
            chat_url = chat_url.replace('//chat/completions', '/chat/completions')
        
        # Basic message payload
        payload = {
            "model": models.get('data', [{}])[0].get('id', 'unknown'),
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one word."}
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        # Make request
        response = requests.post(chat_url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Display response
        completion = response.json()
        if 'choices' in completion and len(completion['choices']) > 0:
            content = completion['choices'][0].get('message', {}).get('content', '')
            print(f"Response: {content}")
            print("✅ Chat completion successful!")
        else:
            print("❌ Chat completion returned unexpected format:")
            print(json.dumps(completion, indent=2))
        
        return True
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure Koboldcpp is running and the URL is correct.")
        return False
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        status_code = e.response.status_code
        if status_code == 401:
            print("Authentication failed. Check your API key.")
        elif status_code == 404:
            print("API endpoint not found. Check the URL.")
        else:
            print(f"Response: {e.response.text}")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Parse command line arguments
    url = "http://localhost:5001/v1"
    api_key = ""
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    if len(sys.argv) > 2:
        api_key = sys.argv[2]
    
    # Test connection
    test_koboldcpp_connection(url, api_key) 