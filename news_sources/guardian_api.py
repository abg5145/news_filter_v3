import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config import GUARDIAN_API_KEY, GUARDIAN_BASE_URL

def fetch_from_guardian(search_terms: List[str], max_results: int = 10) -> List[Dict]:
    """
    Fetch articles from Guardian API (past 2 weeks only)
    
    Args:
        search_terms: List of search terms to query
        max_results: Maximum number of articles to return
        
    Returns:
        List of article dictionaries
    """
    articles = []
    logger = logging.getLogger(__name__)
    logger.info("guardian api function started")
    # Calculate date from 2 weeks ago
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    for term in search_terms:  # Use all search terms (removed [:3] limit)
        try:
            url = f"{GUARDIAN_BASE_URL}/search"
            params = {
                'q': term,
                'api-key': GUARDIAN_API_KEY,
                'page-size': 3,  # Don't divide by search terms
                'order-by': 'relevance',
                'show-fields': 'headline,byline,thumbnail,bodyText,shortUrl',
                'from-date': two_weeks_ago  # Only articles from past 2 weeks
            }
            
            logger.info(f"Guardian API request: term='{term}', page-size=3")
            response = requests.get(url, params=params)
            
            # Log response regardless of status
            response_data = response.json()
            results = response_data.get('response', {}).get('results', [])
            logger.info(f"Guardian API response: {response.status_code}, articles_found={len(results)}, titles={[r.get('fields', {}).get('headline', 'N/A') for r in results[:3]]}")
            
            if response.status_code == 200:
                logger.info(f"Guardian API success: {len(response_data.get('response', {}).get('results', []))} articles returned")
            else:
                logger.error(f"Guardian API error: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            
            for article in data.get('response', {}).get('results', []):
                fields = article.get('fields', {})
                
                # Filter out articles without content
                if fields.get('headline') and fields.get('bodyText'):
                    articles.append({
                        'headline': fields['headline'],
                        'source': 'The Guardian',
                        'author': fields.get('byline', 'Unknown'),
                        'summary': fields['bodyText'][:200] + '...' if len(fields['bodyText']) > 200 else fields['bodyText'],
                        'url': fields.get('shortUrl', article.get('apiUrl')),
                        'image_url': fields.get('thumbnail'),
                        'published_at': article.get('webPublicationDate'),
                        'content': fields['bodyText']
                    })
                    
        except Exception as e:
            continue
    
    return articles[:max_results]
