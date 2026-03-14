import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config import NYTIMES_API_KEY, NYTIMES_BASE_URL

def fetch_from_nytimes(search_terms: List[str], max_results: int = 10) -> List[Dict]:
    """
    Fetch articles from New York Times API (simplified for debugging)
    
    Args:
        search_terms: List of search terms to query
        max_results: Maximum number of articles to return
        
    Returns:
        List of article dictionaries
    """
    articles = []
    
    for term in search_terms[:3]:  # Limit to avoid API rate limits
        try:
            # Simplified API call for debugging
            url = NYTIMES_BASE_URL
            params = {
                'q': term,
                'api-key': NYTIMES_API_KEY,
                'fl': 'headline,snippet,web_url,pub_date',
                'page': 0
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                continue
                
            response.raise_for_status()
            
            data = response.json()
            
            # Check different possible response structures
            if 'response' in data and 'docs' in data['response']:
                docs = data['response']['docs']
            elif 'docs' in data:
                docs = data['docs']
            else:
                docs = []
            
            for article in docs:
                # Simple article processing
                if isinstance(article, dict):
                    headline = article.get('headline', {}).get('main', 'No headline')
                    snippet = article.get('snippet', 'No snippet')
                    web_url = article.get('web_url', 'No URL')
                    pub_date = article.get('pub_date', 'No date')
                    
                    articles.append({
                        'headline': headline,
                        'source': 'The New York Times',
                        'author': 'Unknown',
                        'summary': snippet,
                        'url': web_url,
                        'image_url': None,
                        'published_at': pub_date,
                        'content': snippet
                    })
                    
        except Exception as e:
            continue
    
    return articles[:max_results]
