import json
import requests
from typing import List, Dict, Any, Optional

class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

class LLMInterface:
    def __init__(self, config):
        self.config = config
        self.api_config = config.get_llm_config()['api']
        self.message_config = config.get_llm_config()['message']
        self.character = config.get_character_config()
        self.conversation_history = {}  # channel_id -> List[Message]
    
    def _get_system_prompt(self) -> str:
        """Get system prompt from character config"""
        return self.character['system_prompt']
    
    def reset_conversation(self, channel_id: str) -> None:
        """Reset conversation history for a channel"""
        self.conversation_history[channel_id] = []
    
    def add_message(self, channel_id: str, message: Message) -> None:
        """Add a message to the conversation history"""
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []
        
        self.conversation_history[channel_id].append(message)
        
        # Truncate history if it gets too long
        if len(self.conversation_history[channel_id]) > 20:  # Arbitrary limit, adjust as needed
            self.conversation_history[channel_id] = self.conversation_history[channel_id][-20:]
    
    def get_conversation_history(self, channel_id: str) -> List[Message]:
        """Get conversation history for a channel"""
        return self.conversation_history.get(channel_id, [])
    
    def _build_ollama_payload(self, channel_id: str, user_message: str) -> Dict[str, Any]:
        """Build payload for Ollama API"""
        system_prompt = self._get_system_prompt()
        
        messages = [Message("system", system_prompt)]
        messages.extend(self.get_conversation_history(channel_id))
        messages.append(Message("user", user_message))
        
        return {
            "model": self.api_config['model'],
            "messages": [msg.to_dict() for msg in messages],
            "stream": self.message_config['stream'],
            "options": {
                "temperature": self.message_config['temperature'],
                "top_p": self.message_config['top_p'],
                "max_tokens": self.message_config['max_length']
            }
        }
    
    def query_llm(self, channel_id: str, user_message: str) -> str:
        """Query LLM API with user message and return response"""
        api_url = self.api_config['url']
        
        # Build Ollama payload
        payload = self._build_ollama_payload(channel_id, user_message)
        
        # Standard headers
        headers = {"Content-Type": "application/json"}
        
        # Make API request
        try:
            response = requests.post(api_url, headers=headers, json=payload, stream=self.message_config['stream'])
            response.raise_for_status()
            
            # Handle streaming response
            if self.message_config['stream']:
                return self._handle_streaming_response(response)
            
            # Handle non-streaming response
            return self._handle_non_streaming_response(response)
            
        except requests.exceptions.RequestException as e:
            print(f"Error querying Ollama API: {e}")
            
            error_details = ""
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code == 404:
                    error_details = " The API endpoint could not be found. Check if Ollama is running and available at the URL in config.yaml."
                elif status_code == 400:
                    error_details = " Bad request. Check if your model name is correct."
                elif status_code == 500:
                    error_details = " Ollama server error. Check the Ollama logs for details."
            
            # Return error message with special prefix to indicate it's an error
            return "ERROR:CONNECTION"
    
    def _handle_streaming_response(self, response) -> str:
        """Handle streaming API response from Ollama"""
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    json_line = json.loads(line)
                    if 'message' in json_line and 'content' in json_line['message']:
                        chunk = json_line['message']['content']
                        full_response += chunk
                except json.JSONDecodeError:
                    continue
        
        if not full_response:
            return "ERROR:EMPTY_RESPONSE"
        
        return full_response
    
    def _handle_non_streaming_response(self, response) -> str:
        """Handle non-streaming API response from Ollama"""
        try:
            json_response = response.json()
            content = json_response.get('message', {}).get('content', '')
            
            if not content:
                print(f"Warning: Empty response from Ollama API: {json_response}")
                return "ERROR:EMPTY_RESPONSE"
            
            return content
            
        except json.JSONDecodeError:
            print(f"Error parsing JSON response: {response.text}")
            return "ERROR:PARSE" 