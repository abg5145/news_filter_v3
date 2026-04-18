import logging

logger = logging.getLogger(__name__)

from typing import List, Dict
from news_sources.news_api import fetch_from_news_api
from news_sources.guardian_api import fetch_from_guardian
from news_sources.nytimes_api import fetch_from_nytimes
from news_sources.event_registry_api import fetch_from_event_registry

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
        sources = ['news_api', 'guardian', 'nytimes', 'event_registry']

    all_articles = []

    # Map source names to their respective functions
    source_functions = {
        'news_api': fetch_from_news_api,
        'guardian': fetch_from_guardian,
        'nytimes': fetch_from_nytimes,
        'event_registry': fetch_from_event_registry
    }
    
    # Fetch articles from each specified source
    logger.info(f"DEBUG: Fetching articles from sources: {sources}")
    for source in sources:
        if source in source_functions:
            try:
                logger.info(f"DEBUG: Calling {source} API with search_terms: {search_terms}")
                articles = source_functions[source](search_terms, max_results=10)  # Use all search terms
                logger.info(f"DEBUG: {source} API call completed, returned {len(articles)} articles")
                all_articles.extend(articles)
                logger.info(f"DEBUG: {source} returned {len(articles)} articles")
                # Log articles from this source
                if articles:
                    article_list = []
                    for article in articles:
                        # Handle different field names from different APIs
                        title = (article.get('headline') or 
                                article.get('title') or 
                                article.get('headline', {}).get('main', 'N/A'))
                        
                        date = (article.get('published_at') or 
                               article.get('publishedAt') or 
                               article.get('pub_date') or 
                               article.get('webPublicationDate', 'N/A'))
                        
                        # Ensure both are strings
                        title_str = str(title) if title and title != 'N/A' else 'N/A'
                        date_str = str(date) if date and date != 'N/A' else 'N/A'
                        article_list.append(f"{title_str} - {date_str}")
                    
                    logger.info(f"Articles from {source}: " + " | ".join(article_list))
                else:
                    logger.info(f"DEBUG: {source} returned no articles")
            
            except Exception as e:
                logger.error(f"DEBUG: {source} API failed: {e}")
                import traceback
                logger.error(f"DEBUG: {source} API traceback: {traceback.format_exc()}")
                continue
    
    # Remove duplicates based on URL, but keep articles without URLs too
    logger.info(f"DEBUG: Total raw articles collected: {len(all_articles)}")
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        article_url = article.get('url')
        if article_url and article_url not in seen_urls:
            seen_urls.add(article_url)
            unique_articles.append(article)
        elif not article_url:  # Keep articles without URLs
            unique_articles.append(article)
    
    logger.info(f"DEBUG: Articles after deduplication: {len(unique_articles)}")
    
    # Sort by publication date if available, otherwise keep original order
    unique_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    
    return unique_articles[:30]  # Return max 30 articles as specified
