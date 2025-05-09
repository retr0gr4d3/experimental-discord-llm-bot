#!/usr/bin/env python3
"""
This script tests the connection to your LLM API.
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
        
        return False

def test_koboldcpp_connection(config):
    """Test connection to KoboldCPP API"""
    api_url = config['llm']['api']['url']
    
    print(f"Testing connection to KoboldCPP API at {api_url}...")
    
    payload = {
        "prompt": "Hello, are you working?",
        "max_length": 50
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        print(f"✅ Successfully connected to KoboldCPP API!")
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to KoboldCPP API: {e}")
        
        if "Connection refused" in str(e):
            print("\nPossible solutions:")
            print("1. Make sure KoboldCPP is installed and running")
            print("2. Check if the API URL is correct (typically http://localhost:5001/api/v1/generate)")
        
        return False

def test_openai_connection(config):
    """Test connection to OpenAI API"""
    api_url = config['llm']['api']['url']
    api_key = config['llm']['api']['key']
    model = config['llm']['api']['model']
    
    if not api_key:
        print("❌ Error: OpenAI API key is missing in config.yaml")
        print("Please add your OpenAI API key to the config.yaml file.")
        return False
    
    print(f"Testing connection to OpenAI API at {api_url}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, are you working?"}
        ]
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"✅ Successfully connected to OpenAI API!")
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to OpenAI API: {e}")
        
        if "401" in str(e):
            print("\nPossible solutions:")
            print("1. Check if your API key is correct")
            print("2. Make sure your OpenAI account has billing set up")
        
        return False

def main():
    """Main function"""
    config = load_config()
    api_type = config['llm']['api']['type']
    
    if api_type == 'ollama':
        test_ollama_connection(config)
    elif api_type == 'koboldcpp':
        test_koboldcpp_connection(config)
    elif api_type == 'openai':
        test_openai_connection(config)
    else:
        print(f"❌ Unsupported API type: {api_type}")
        print("Supported types: ollama, koboldcpp, openai")
        sys.exit(1)

if __name__ == "__main__":
    main() 