import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config import NEWS_API_KEY, NEWS_API_BASE_URL

def fetch_from_news_api(search_terms: List[str], max_results: int = 10) -> List[Dict]:
    """
    Fetch articles from News API (past 2 weeks only)
    
    Args:
        search_terms: List of search terms to query
        max_results: Maximum number of articles to return
        
    Returns:
        List of article dictionaries
    """
    logger = logging.getLogger(__name__)
    logger.info("news api function started")
    articles = []
    
    # Calculate date from 2 weeks ago
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    for term in search_terms:  # Limit to avoid API rate limits
        try:
            logger.info(f"news api processing term: {term}")
            url = f"{NEWS_API_BASE_URL}/everything"
            params = {
                'q': term,
                'apiKey': NEWS_API_KEY,
                'pageSize': 3,  # Don't divide by search terms
                'sortBy': 'relevancy',
                'language': 'en',
                'from': two_weeks_ago  # Only articles from past 2 weeks
            }
            
            logger.info(f"News API request: term='{term}', pageSize=3")
            response = requests.get(url, params=params)
            
            # Log response regardless of status
            response_data = response.json()
            articles_list = response_data.get('articles', [])
            logger.info(f"News API response: {response.status_code}, articles_found={len(articles_list)}, titles={[a.get('title', 'N/A') for a in articles_list[:3]]}")
            
            if response.status_code == 200:
                logger.info(f"News API success: {len(response_data.get('articles', []))} articles returned")
            else:
                logger.error(f"News API error: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            
            for article in data.get('articles', []):
                # Filter out articles without content
                if article.get('description') and article.get('title'):
                    articles.append({
                        'headline': article['title'],
                        'source': article['source']['name'],
                        'author': article.get('author', 'Unknown'),
                        'summary': article['description'],
                        'url': article['url'],
                        'image_url': article.get('urlToImage'),
                        'published_at': article.get('publishedAt'),
                        'content': article['description']  # News API doesn't provide full content
                    })
            
            logger.info(f"DEBUG: News API term '{term}' processed, running total: {len(articles)} articles")
                    
        except Exception as e:
            logger.error(f"DEBUG: News API term '{term}' failed: {e}")
            import traceback
            logger.error(f"DEBUG: News API traceback: {traceback.format_exc()}")
            continue
    
    logger.info(f"DEBUG: News API returning {len(articles[:max_results])} articles (raw: {len(articles)}, max_results: {max_results})")
    return articles[:max_results]
