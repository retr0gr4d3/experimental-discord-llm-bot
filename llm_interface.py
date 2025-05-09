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
    
    def _build_koboldcpp_payload(self, channel_id: str, user_message: str) -> Dict[str, Any]:
        """Build payload for KoboldCPP API"""
        system_prompt = self._get_system_prompt()
        
        # Format prompt for KoboldCPP
        prompt = f"{system_prompt}\n\n"
        
        for msg in self.get_conversation_history(channel_id):
            if msg.role == "user":
                prompt += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                prompt += f"Assistant: {msg.content}\n"
        
        prompt += f"User: {user_message}\nAssistant:"
        
        return {
            "prompt": prompt,
            "max_length": self.message_config['max_length'],
            "temperature": self.message_config['temperature'],
            "top_p": self.message_config['top_p'],
            "stream": self.message_config['stream']
        }
    
    def _build_openai_payload(self, channel_id: str, user_message: str) -> Dict[str, Any]:
        """Build payload for OpenAI-compatible API"""
        system_prompt = self._get_system_prompt()
        
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in self.get_conversation_history(channel_id):
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": user_message})
        
        return {
            "model": self.api_config['model'],
            "messages": messages,
            "temperature": self.message_config['temperature'],
            "max_tokens": self.message_config['max_length'],
            "top_p": self.message_config['top_p'],
            "stream": self.message_config['stream']
        }
    
    def _get_api_headers(self) -> Dict[str, str]:
        """Get headers for API request"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key if configured
        if self.api_config['key']:
            if self.api_config['type'] == 'openai':
                headers["Authorization"] = f"Bearer {self.api_config['key']}"
            else:
                headers["x-api-key"] = self.api_config['key']
        
        return headers
    
    def query_llm(self, channel_id: str, user_message: str) -> str:
        """Query LLM API with user message and return response"""
        api_url = self.api_config['url']
        api_type = self.api_config['type']
        
        # Build payload based on API type
        if api_type == 'ollama':
            payload = self._build_ollama_payload(channel_id, user_message)
        elif api_type == 'koboldcpp':
            payload = self._build_koboldcpp_payload(channel_id, user_message)
        elif api_type == 'openai':
            payload = self._build_openai_payload(channel_id, user_message)
        else:
            raise ValueError(f"Unsupported API type: {api_type}")
        
        headers = self._get_api_headers()
        
        # Make API request
        try:
            response = requests.post(api_url, headers=headers, json=payload, stream=self.message_config['stream'])
            response.raise_for_status()
            
            # Handle streaming response
            if self.message_config['stream']:
                return self._handle_streaming_response(response, api_type)
            
            # Handle non-streaming response
            return self._handle_non_streaming_response(response, api_type)
            
        except requests.exceptions.RequestException as e:
            print(f"Error querying LLM API: {e}")
            return "I'm sorry, I'm having trouble connecting to my language model right now. Please try again later."
    
    def _handle_streaming_response(self, response, api_type: str) -> str:
        """Handle streaming API response"""
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                if api_type == 'ollama':
                    try:
                        json_line = json.loads(line)
                        if 'message' in json_line and 'content' in json_line['message']:
                            chunk = json_line['message']['content']
                            full_response += chunk
                    except json.JSONDecodeError:
                        continue
                elif api_type == 'openai':
                    try:
                        # Skip "data: " prefix
                        if line.startswith(b'data: '):
                            line = line[6:]
                        if line.strip() == b'[DONE]':
                            continue
                        json_line = json.loads(line)
                        if 'choices' in json_line and len(json_line['choices']) > 0:
                            delta = json_line['choices'][0].get('delta', {})
                            if 'content' in delta:
                                full_response += delta['content']
                    except json.JSONDecodeError:
                        continue
                elif api_type == 'koboldcpp':
                    try:
                        json_line = json.loads(line)
                        if 'token' in json_line:
                            full_response += json_line['token']
                    except json.JSONDecodeError:
                        continue
        
        return full_response
    
    def _handle_non_streaming_response(self, response, api_type: str) -> str:
        """Handle non-streaming API response"""
        json_response = response.json()
        
        if api_type == 'ollama':
            return json_response.get('message', {}).get('content', '')
        elif api_type == 'openai':
            return json_response.get('choices', [{}])[0].get('message', {}).get('content', '')
        elif api_type == 'koboldcpp':
            return json_response.get('results', [{}])[0].get('text', '')
        
        return "" 