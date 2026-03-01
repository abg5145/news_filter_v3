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
                print(f"Fetching articles from {source}...")
                articles = source_functions[source](search_terms, max_results=10)
                print(f"Successfully fetched {len(articles)} articles from {source}:")
                for i, article in enumerate(articles, 1):
                    print(f"  {i}. Title: {article.get('headline', 'N/A')}")
                    print(f"     Source: {article.get('source', 'N/A')}")
                    print(f"     URL: {article.get('url', 'N/A')}")
                    print()
                all_articles.extend(articles)
                print(f"Total from {source}: {len(articles)} articles")
                print("-" * 50)
            except Exception as e:
                print(f"Failed to fetch from {source}: {e}")
                continue
        else:
            print(f"Unknown source: {source}")
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article.get('url') and article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)
    
    # Sort by publication date if available, otherwise keep original order
    unique_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    
    print(f"\nFinal unique articles after deduplication: {len(unique_articles)}")
    print("Final article list:")
    for i, article in enumerate(unique_articles[:10], 1):
        print(f"  {i}. Title: {article.get('headline', 'N/A')}")
        print(f"     Source: {article.get('source', 'N/A')}")
        print(f"     Published: {article.get('published_at', 'N/A')}")
        print()
    
    return unique_articles[:10]  # Return max 10 articles as specified
