from utils.openai_client import OpenAIClient
from config import CHEAP_MODEL

def generate_search_terms(article_text: str) -> dict:
    """
    First ChatGPT call: Generate search terms from article text
    Uses cheaper model (gpt-3.5-turbo)
    
    Args:
        article_text: The original article text
        
    Returns:
        Dictionary with search terms and metadata
    """
    client = OpenAIClient()
    
    prompt = f"""
    Analyze the following article text and generate 3 relevant search terms that would help find similar articles from different news sources.
    Focus on key topics, people, events, and locations mentioned.
    Return the search terms as a comma-separated list.

    Article text:
    {article_text}
    """
    
    messages = [
        {"role": "system", "content": "You are a research assistant that extracts key search terms from news articles."},
        {"role": "user", "content": prompt}
    ]
    
    response = client.call_chatgpt(CHEAP_MODEL, messages, temperature=0.3)
    
    if response["success"]:
        # Parse the comma-separated search terms
        search_terms = [term.strip() for term in response["content"].split(",")]
        return {
            "success": True,
            "search_terms": search_terms,
            "raw_response": response["content"]
        }
    else:
        return {
            "success": False,
            "error": response["error"]
        }
