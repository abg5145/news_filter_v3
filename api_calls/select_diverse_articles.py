from utils.openai_client import OpenAIClient
from config import CHEAP_MODEL

def select_diverse_articles(article_summaries: list, original_article: str = "") -> dict:
    """
    Second ChatGPT call: Select top 3 articles with differing viewpoints
    Uses cheaper model (gpt-3.5-turbo)
    
    Args:
        article_summaries: List of article summaries from different sources
        original_article: The original article text for context
        
    Returns:
        Dictionary with selected articles and analysis
    """
    client = OpenAIClient()
    
    # Format summaries for the prompt
    formatted_summaries = ""
    for i, summary in enumerate(article_summaries, 1):
        formatted_summaries += f"Article {i}:\n"
        formatted_summaries += f"Headline: {summary.get('headline', 'N/A')}\n"
        formatted_summaries += f"Source: {summary.get('source', 'N/A')}\n"
        formatted_summaries += f"Summary: {summary.get('summary', 'N/A')}\n\n"
    
    prompt = f"""
    You are selecting diverse articles that cover the SAME topic as the original article.
    
    Original Article Topic:
    {original_article[:500]}...
    
    Available Article Summaries:
    {formatted_summaries}
    
    Your task: Select exactly 3 articles that:
    1. Cover the SAME topic/event/issue as the original article
    2. Represent different viewpoints or perspectives (liberal, conservative, centrist, different geographic focus, etc.)
    3. Are from credible news sources
    
    Consider differences in:
    - Political leaning (liberal, conservative, centrist)
    - Geographic focus (local, national, international)
    - Tone and framing (positive, negative, neutral)
    - Emphasis on different aspects of the story
    
    IMPORTANT: Only select articles that are clearly about the same topic. If an article is about a different topic, do not select it.
    
    Return your response as valid JSON only. Do not include any text before or after the JSON:
    {{
        "selected_articles": [
            {{
                "article_index": 1,
                "reason": "Brief explanation of why this article was selected and how it relates to the original topic",
                "viewpoint": "Description of the perspective this represents (e.g., liberal, conservative, centrist, international, local)"
            }},
            ...
        ],
        "analysis": "Brief summary of how the selected articles provide diverse perspectives on the same topic"
    }}
    
    IMPORTANT: Return ONLY valid JSON. No explanations, no markdown formatting, just the JSON object.
    """
    
    messages = [
        {"role": "system", "content": "You are a media analyst that identifies diverse perspectives in news coverage."},
        {"role": "user", "content": prompt}
    ]
    
    response = client.call_chatgpt(CHEAP_MODEL, messages, temperature=0.5)
    
    if response["success"]:
        try:
            import json
            import re
            
            # Try to extract JSON from the response
            content = response["content"].strip()
            
            # Look for JSON object in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                # If no JSON found, try parsing the entire response
                result = json.loads(content)
                
            return {
                "success": True,
                "selected_articles": result.get("selected_articles", []),
                "analysis": result.get("analysis", ""),
                "raw_response": response["content"]
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_response": response["content"]
            }
    else:
        return {
            "success": False,
            "error": response["error"]
        }
