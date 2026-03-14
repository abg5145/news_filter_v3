import logging

logger = logging.getLogger(__name__)

from typing import List, Dict
from news_sources.news_api import fetch_from_news_api
from news_sources.guardian_api import fetch_from_guardian
from news_sources.nytimes_api import fetch_from_nytimes

def fetch_articles_from_sources(search_terms: List[str], sources: List[str] = None) -> List[Dict]:
    """
    Single function for fetching articles from multiple news sources
    
    Args:
        search_terms: List of search terms to query
        sources: List of news sources to fetch from (default: all available)
        
    Returns:
        Combined list of articles from all sources
    """
    if sources is None:
        sources = ['news_api', 'guardian', 'nytimes']
    
    all_articles = []
    
    # Map source names to their respective functions
    source_functions = {
        'news_api': fetch_from_news_api,
        'guardian': fetch_from_guardian,
        'nytimes': fetch_from_nytimes
    }
    
    # Fetch articles from each specified source
    for source in sources:
        if source in source_functions:
            try:
                articles = source_functions[source](search_terms, max_results=10)
                all_articles.extend(articles)
                
                # Log articles from this source
                if articles:
                    article_list = []
                    for article in articles:
                        title = article.get('headline', 'N/A')
                        date = article.get('published_at', 'N/A')
                        # Ensure both are strings
                        title_str = str(title) if title else 'N/A'
                        date_str = str(date) if date else 'N/A'
                        article_list.append(f"{title_str} - {date_str}")
                    
                    logger.info(f"Articles from {source}:\n" + "\n".join(article_list))
            except Exception as e:
                continue
        else:
            continue
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article.get('url') and article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)
    
    # Sort by publication date if available, otherwise keep original order
    unique_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    
    return unique_articles[:10]  # Return max 10 articles as specified
