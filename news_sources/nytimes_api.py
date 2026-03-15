import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config import NYTIMES_API_KEY, NYTIMES_BASE_URL

def fetch_from_nytimes(search_terms: List[str], max_results: int = 10) -> List[Dict]:
    """
    Fetch articles from New York Times API
    
    Args:
        search_terms: List of search terms to query
        max_results: Maximum number of articles to return
        
    Returns:
        List of article dictionaries
    """
    articles = []
    logger = logging.getLogger(__name__)
    logger.info("nytimes api function started")
    
    for term in search_terms:  # Limit to avoid API rate limits
        try:
            # Simplified API call for debugging
            url = NYTIMES_BASE_URL
            params = {
                'q': term,
                'api-key': NYTIMES_API_KEY,
                'fl': 'headline,snippet,web_url,pub_date',
                'page': 0
            }
            
            logger.info(f"NY Times API request: term='{term}', page=0")
            response = requests.get(url, params=params)
            
            # Log response regardless of status
            response_data = response.json()
            docs = response_data.get('response', {}).get('docs', [])
            
            # Limit to first 3 articles from the API response
            docs = docs[:3]
            logger.info(f"NY Times API response: {response.status_code}, articles_found={len(docs)}, titles={[d.get('headline', {}).get('main', 'N/A') for d in docs]}")
            
            if response.status_code == 200:
                logger.info(f"NY Times API success: {len(docs)} articles returned")
            else:
                logger.error(f"NY Times API error: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            
            # Check different possible response structures
            if 'response' in data and 'docs' in data['response']:
                all_docs = data['response']['docs']
            elif 'docs' in data:
                all_docs = data['docs']
            else:
                all_docs = []
            
            # Use the already limited docs (first 3)
            docs = all_docs[:3]
            
            # Limit to 3 articles per search term
            docs = docs[:3]
            
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
