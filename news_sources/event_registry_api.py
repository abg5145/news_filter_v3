import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config import EVENT_REGISTRY_API_KEY, EVENT_REGISTRY_BASE_URL

def fetch_from_event_registry(search_terms: List[str], max_results: int = 10) -> List[Dict]:
    logger = logging.getLogger(__name__)
    logger.info("event registry api function started")
    articles = []

    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')

    for term in search_terms:
        try:
            logger.info(f"event registry processing term: {term}")
            url = f"{EVENT_REGISTRY_BASE_URL}/article/getArticles"
            payload = {
                'action': 'getArticles',
                'keyword': term,
                'apiKey': EVENT_REGISTRY_API_KEY,
                'dateStart': one_week_ago,
                'dateEnd': today,
                'startSourceRankPercentile': 0,
                'endSourceRankPercentile': 30,
                'articlesCount': 3,
                'articlesSortBy': 'rel',
                'lang': 'eng',
                'resultType': 'articles',
                'articleBodyLen': -1
            }

            logger.info(f"Event Registry request: term='{term}', dateStart={one_week_ago}, sourceRankPercentile=0-30")
            response = requests.post(url, json=payload)

            response_data = response.json()
            results = response_data.get('articles', {}).get('results', [])
            logger.info(f"Event Registry response: {response.status_code}, articles_found={len(results)}, titles={[a.get('title', 'N/A') for a in results[:3]]}")

            if response.status_code != 200:
                logger.error(f"Event Registry error: {response.status_code} - {response.text}")
                response.raise_for_status()

            for article in results:
                if article.get('title') and article.get('body'):
                    body = article.get('body', '')
                    source = article.get('source', {})
                    authors = article.get('authors', [])
                    articles.append({
                        'headline': article['title'],
                        'source': source.get('title', 'Unknown'),
                        'author': ', '.join(a.get('name', '') for a in authors) or 'Unknown',
                        'summary': body[:200] + '...' if len(body) > 200 else body,
                        'url': article.get('url'),
                        'image_url': article.get('image'),
                        'published_at': article.get('dateTime'),
                        'content': body
                    })

            logger.info(f"Event Registry term '{term}' processed, running total: {len(articles)} articles")

        except Exception as e:
            logger.error(f"Event Registry term '{term}' failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            continue

    logger.info(f"Event Registry returning {len(articles[:max_results])} articles (raw: {len(articles)}, max_results: {max_results})")
    return articles[:max_results]
