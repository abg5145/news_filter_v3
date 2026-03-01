import openai
import json
from typing import Dict, Any
from config import OPENAI_API_KEY, OPENAI_BASE_URL

class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
    
    def call_chatgpt(self, model: str, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Common abstract function for ChatGPT API calls
        
        Args:
            model: ChatGPT model to use
            messages: List of message dictionaries
            temperature: Temperature for response generation
            
        Returns:
            Dictionary containing the response content and metadata
        """
        print(f"\n=== ChatGPT API Call ===")
        print(f"Model: {model}")
        print(f"Temperature: {temperature}")
        print(f"Messages:")
        for i, msg in enumerate(messages):
            print(f"  {i+1}. Role: {msg['role']}")
            print(f"     Content (full):")
            print(f"     {msg['content']}")
            print(f"     --- End of Message {i+1} ---")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            print(f"\nResponse: {content}")
            print(f"Usage: {response.usage}")
            print("=" * 50)
            
            return {
                "success": True,
                "content": content,
                "usage": response.usage,
                "model": model
            }
        except Exception as e:
            print(f"Error: {e}")
            print("=" * 50)
            return {
                "success": False,
                "error": str(e),
                "model": model
            }
