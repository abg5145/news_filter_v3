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
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            return {
                "success": True,
                "content": content,
                "usage": response.usage,
                "model": model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model
            }
