from utils.openai_client import OpenAIClient
from config import ADVANCED_MODEL

def analyze_article(original_article: str, diverse_articles: list) -> dict:
    """
    Third ChatGPT call: Analyze original article for facts, opinions, biases, and GenAI score
    Uses advanced model (GPT-4o)
    
    Args:
        original_article: The original article text
        diverse_articles: List of selected diverse articles with their content
        
    Returns:
        Dictionary with comprehensive analysis
    """
    client = OpenAIClient()
    
    # Format diverse articles for comparison
    formatted_articles = ""
    for i, article in enumerate(diverse_articles, 1):
        formatted_articles += f"Comparison Article {i}:\n"
        formatted_articles += f"Headline: {article.get('headline', 'N/A')}\n"
        formatted_articles += f"Source: {article.get('source', 'N/A')}\n"
        formatted_articles += f"Content: {article.get('content', 'N/A')}\n\n"
    
    prompt = f"""
    Perform a comprehensive analysis of the original article by comparing it with the diverse perspectives from other sources.
    
    Original Article:
    {original_article}
    
    Comparison Articles:
    {formatted_articles}
    
    Provide a detailed analysis in valid JSON format only. Do not include any text before or after the JSON:
    {{
        "key_facts": [
            {{
                "fact": "Statement of the fact",
                "verification": "How it's supported by comparison articles",
                "confidence": "high/medium/low"
            }},
            ...
        ],
        "opinions": [
            {{
                "statement": "Identified opinion or subjective statement",
                "context": "Where this appears in the article",
                "bias_indication": "liberal/conservative/centrist/other"
            }},
            ...
        ],
        "biases": [
            {{
                "type": "selection_bias/framing_bias/wording_bias/omission_bias",
                "description": "How this bias manifests",
                "impact": "How it affects reader perception"
            }},
            ...
        ],
        "genai_analysis": {{
            "genai_probability_score": 0-100,
            "reasoning": "Why this score was given",
            "telltales": ["List of indicators suggesting AI generation"]
        }},
        "overall_assessment": "Brief summary of the article's credibility and perspective"
    }}
    
    Focus on:
    - Factual accuracy compared to other sources
    - Subjective language and framing
    - What's included vs. omitted
    - Linguistic patterns that might indicate AI generation
    - Consistency with established journalistic practices
    
    IMPORTANT: Return ONLY valid JSON. No explanations, no markdown formatting, just the JSON object.
    """
    
    messages = [
        {"role": "system", "content": "You are an expert media analyst and fact-checker with expertise in identifying bias and AI-generated content."},
        {"role": "user", "content": prompt}
    ]
    
    response = client.call_chatgpt(ADVANCED_MODEL, messages, temperature=0.2)
    
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
                "analysis": result,
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
