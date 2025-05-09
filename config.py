import os
import json
import yaml
from dotenv import load_dotenv

class Config:
    def __init__(self, config_file="config.yaml", character_file=None):
        # Load environment variables
        load_dotenv()
        
        # Load configuration from YAML
        self.config = self._load_yaml_config(config_file)
        
        # Override token with env var if available
        if not self.config['discord']['token'] and os.getenv('DISCORD_TOKEN'):
            self.config['discord']['token'] = os.getenv('DISCORD_TOKEN')
            
        # Load character configuration
        character_path = character_file or self.config['character']['path']
        self.character = self._load_character_config(character_path)
    
    def _load_yaml_config(self, config_file):
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
            return self._default_config()
    
    def _load_character_config(self, character_file):
        """Load character configuration from JSON file"""
        try:
            with open(character_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading character file: {e}")
            return self._default_character()
    
    def _default_config(self):
        """Return default configuration"""
        return {
            'discord': {
                'token': '',
                'command_prefix': '/'
            },
            'llm': {
                'api': {
                    'url': 'http://localhost:11434/api/chat',
                    'key': '',
                    'type': 'ollama',
                    'model': 'llama3'
                },
                'message': {
                    'max_context_length': 4096,
                    'max_length': 800,
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'stream': True
                }
            },
            'character': {
                'path': 'character.json'
            }
        }
    
    def _default_character(self):
        """Return default character configuration"""
        return {
            'name': 'Assistant',
            'description': 'A helpful AI assistant.',
            'personality': 'Helpful and friendly.',
            'greeting': 'Hello! How can I help you?',
            'example_conversations': [],
            'system_prompt': 'You are a helpful AI assistant.'
        }
    
    def get_discord_token(self):
        """Get Discord bot token"""
        return self.config['discord']['token']
    
    def get_command_prefix(self):
        """Get command prefix"""
        return self.config['discord']['command_prefix']
    
    def get_llm_config(self):
        """Get LLM configuration"""
        return self.config['llm']
    
    def get_character_config(self):
        """Get character configuration"""
        return self.character
    
    def get_system_prompt(self):
        """Get system prompt for the LLM"""
        return self.character['system_prompt'] 