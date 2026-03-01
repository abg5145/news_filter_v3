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
    articles = []
    
    # Calculate date from 2 weeks ago
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    for term in search_terms[:3]:  # Limit to avoid API rate limits
        try:
            url = f"{NEWS_API_BASE_URL}/everything"
            params = {
                'q': term,
                'apiKey': NEWS_API_KEY,
                'pageSize': min(max_results // len(search_terms), 5),
                'sortBy': 'relevancy',
                'language': 'en',
                'from': two_weeks_ago  # Only articles from past 2 weeks
            }
            
            response = requests.get(url, params=params)
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
                    
        except Exception as e:
            print(f"Error fetching from News API for term '{term}': {e}")
            continue
    
    return articles[:max_results]
