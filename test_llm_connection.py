#!/usr/bin/env python3
"""
This script tests the connection to the Ollama API.
Run it with: python test_llm_connection.py
"""

import json
import requests
import yaml
import sys

def load_config():
    """Load configuration from YAML file"""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def test_ollama_connection(config):
    """Test connection to Ollama API"""
    api_url = config['llm']['api']['url']
    model = config['llm']['api']['model']
    
    print(f"Testing connection to Ollama API at {api_url}...")
    print(f"Using model: {model}")
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, are you working?"}
        ]
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        print(f"✅ Successfully connected to Ollama API!")
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Ollama API: {e}")
        
        if "Connection refused" in str(e):
            print("\nPossible solutions:")
            print("1. Make sure Ollama is installed and running")
            print("2. Check if Ollama is running with: ps aux | grep ollama")
            print("3. Start Ollama if needed")
            print("4. Make sure you've pulled the model with: ollama pull", model)
        elif "404" in str(e):
            print("\nPossible solutions:")
            print("1. Check if the API URL is correct")
            print("2. For Ollama, the API URL should typically be: http://localhost:11434/api/chat")
            print("3. Make sure Ollama is running and responding to API requests")
        elif "400" in str(e):
            print("\nPossible solutions:")
            print(f"1. Check if the model '{model}' exists in Ollama")
            print(f"2. Pull the model with: ollama pull {model}")
        
        return False

def main():
    """Main function"""
    config = load_config()
    test_ollama_connection(config)

if __name__ == "__main__":
    main() 