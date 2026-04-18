import os
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Reduce noisy library logs
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

from flask import Flask, render_template, request, jsonify
from api_calls.generate_search_terms import generate_search_terms
from api_calls.select_diverse_articles import select_diverse_articles
from api_calls.analyze_article import analyze_article
from utils.article_fetcher import fetch_articles_from_sources
from config import (DYNAMODB_TABLE_NAME, DYNAMODB_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

app = Flask(__name__)

logger = logging.getLogger(__name__)

def is_running_on_aws():
    """Check if the app is running on AWS"""
    return os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None or os.environ.get("ECS_CONTAINER_METADATA_URI") is not None

def record_user_request_to_dynamodb(search_terms, user_ip, all_articles, top_5_articles, chatgpt_response):
    """Record user request data to DynamoDB"""
    if not is_running_on_aws():
        logger.info("Skipping DynamoDB recording - not running on AWS")
        return
    
    try:
        import boto3
        
        # Initialize DynamoDB client
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=DYNAMODB_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        # Create timestamp for unique ID
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        def strip_content(articles):
            return [{k: v for k, v in a.items() if k != 'content'} for a in articles]

        # Prepare the item to insert
        item = {
            'request_id': timestamp,  # Using timestamp as unique ID
            'timestamp': timestamp,
            'search_terms': json.dumps(search_terms),
            'user_ip_address': user_ip,
            'all_articles': json.dumps(strip_content(all_articles)),
            'top_5_articles': json.dumps(strip_content(top_5_articles)),
            'chatgpt_response': json.dumps(chatgpt_response)
        }
        
        # Insert item into DynamoDB
        table.put_item(Item=item)
        logger.info(f"Successfully recorded request to DynamoDB with ID: {timestamp}")
        
    except Exception as e:
        logger.error(f"Failed to record request to DynamoDB: {e}")
        # Don't raise the exception to avoid breaking the main functionality

@app.route('/')
def index():
    """Main page with article input form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_article_endpoint():
    """
    Main endpoint that processes the article through the complete pipeline
    """
    try:
        # Get article text from request
        data = request.get_json()
        article_text = data.get('article_text', '')
        
        if not article_text.strip():
            return jsonify({
                'success': False,
                'error': 'Article text is required'
            }), 400
        
        # Step 1: Generate search terms using ChatGPT (cheaper model)
        logger.info(f"DEBUG: Starting search term generation for article length: {len(article_text)}")
        search_result = generate_search_terms(article_text)
        if not search_result['success']:
            logger.error(f"DEBUG: Search term generation failed: {search_result.get('error', 'Unknown error')}")
            return jsonify({
                'success': False,
                'error': f"Failed to generate search terms: {search_result['error']}"
            }), 500
        
        search_terms = search_result['search_terms']
        logger.info(f"DEBUG: Generated search terms: {search_terms}")
        search_terms_str = ', '.join([str(term) for term in search_terms])
        logger.info(f"Search terms derived: {search_terms_str}")
        
        # Step 2: Fetch articles from at least 3 news sources
        logger.info(f"DEBUG: Starting article fetching with search terms: {search_terms}")
        articles = fetch_articles_from_sources(search_terms, ['news_api', 'guardian', 'nytimes', 'event_registry'])
        logger.info(f"DEBUG: Fetched {len(articles)} articles total")
        
        if len(articles) < 5:
            logger.error(f"DEBUG: Not enough articles fetched, only {len(articles)}")
            return jsonify({
                'success': False,
                'error': f"Could not fetch enough articles. Only found {len(articles)} articles."
            }), 500
        
        # Step 3: Select top 5 articles with differing viewpoints using ChatGPT (cheaper model)
        diverse_result = select_diverse_articles(articles, article_text)
        if not diverse_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to select diverse articles: {diverse_result['error']}"
            }), 500
        
        selected_indices = [article['article_index'] - 1 for article in diverse_result['selected_articles']]
        diverse_articles = [articles[i] for i in selected_indices if i < len(articles)]
        
        # Log top 5 articles selected for comparison
        articles_info = []
        for i, article in enumerate(diverse_articles, 1):
            headline = str(article.get('headline', 'N/A'))
            source = str(article.get('source', 'N/A'))
            published_at = str(article.get('published_at', 'N/A'))
            articles_info.append(
                f"{i}. {headline} - {source} - {published_at} - Selected for diverse viewpoint"
            )
        logger.info("Top 5 articles selected for comparison: " + " | ".join(articles_info))
        
        # Step 4: Analyze original article with diverse articles using ChatGPT (advanced model)
        analysis_result = analyze_article(article_text, diverse_articles)
        if not analysis_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to analyze article: {analysis_result['error']}"
            }), 500
        
        logger.info("Analysis complete!")
        
        logger.info("DEBUG: About to start logging section...")
        try:
            logger.info("DEBUG: Entered try block for logging section...")
            # Debug: Check the structure of analysis_result
            logger.info(f"DEBUG: analysis_result type: {type(analysis_result)}")
            logger.info(f"DEBUG: analysis_result keys: {list(analysis_result.keys()) if isinstance(analysis_result, dict) else 'Not a dict'}")
            
            if 'analysis' in analysis_result:
                analysis = analysis_result['analysis']
                logger.info(f"DEBUG: analysis type: {type(analysis)}")
                logger.info(f"DEBUG: analysis keys: {list(analysis.keys()) if isinstance(analysis, dict) else 'Not a dict'}")
            else:
                logger.error("DEBUG: No 'analysis' key in analysis_result")
                logger.error(f"DEBUG: Full analysis_result: {analysis_result}")
                return jsonify({
                    'success': False,
                    'error': "Invalid analysis result structure"
                }), 500
            
            # Build comprehensive findings summary
            findings_parts = []
            
            if analysis.get('overall_assessment'):
                overall_str = str(analysis['overall_assessment'])
                findings_parts.append(f"Overall Assessment: {overall_str}")
            
            if analysis.get('key_facts'):
                key_facts = analysis['key_facts']
                logger.info(f"DEBUG: key_facts type: {type(key_facts)} - {key_facts}")
                if isinstance(key_facts, list):
                    key_facts_list = []
                    for fact in key_facts:
                        if isinstance(fact, dict):
                            # Extract the main fact from dictionary
                            fact_str = fact.get('fact', str(fact))
                        else:
                            fact_str = str(fact)
                        key_facts_list.append(fact_str)
                    key_facts_str = '; '.join(key_facts_list)
                else:
                    key_facts_str = str(key_facts)
                findings_parts.append(f"Key Facts: {key_facts_str}")
            
            if analysis.get('opinions'):
                opinions = analysis['opinions']
                logger.info(f"DEBUG: opinions type: {type(opinions)} - {opinions}")
                if isinstance(opinions, list):
                    opinions_list = []
                    for opinion in opinions:
                        if isinstance(opinion, dict):
                            # Extract the statement from dictionary
                            opinion_str = opinion.get('statement', str(opinion))
                        else:
                            opinion_str = str(opinion)
                        opinions_list.append(opinion_str)
                    opinions_str = '; '.join(opinions_list)
                else:
                    opinions_str = str(opinions)
                findings_parts.append(f"Opinions: {opinions_str}")
            
            if analysis.get('biases'):
                biases = analysis['biases']
                logger.info(f"DEBUG: biases type: {type(biases)} - {biases}")
                if isinstance(biases, list):
                    biases_list = []
                    for bias in biases:
                        if isinstance(bias, dict):
                            # Extract the description from dictionary
                            bias_str = bias.get('description', str(bias))
                        else:
                            bias_str = str(bias)
                        biases_list.append(bias_str)
                    biases_str = '; '.join(biases_list)
                else:
                    biases_str = str(biases)
                findings_parts.append(f"Biases: {biases_str}")
            
            if analysis.get('genai_analysis'):
                genai = analysis['genai_analysis']
                logger.info(f"DEBUG: genai type: {type(genai)} - {genai}")
                if genai.get('genai_probability_score'):
                    findings_parts.append(f"GenAI Probability: {str(genai['genai_probability_score'])}%")
                if genai.get('reasoning'):
                    findings_parts.append(f"GenAI Reasoning: {str(genai['reasoning'])}")
            
            logger.info("Complete ChatGPT Analysis: " + " | ".join(findings_parts))
            
        except Exception as e:
            logger.error(f"DEBUG: Error in logging section: {e}")
            logger.error(f"DEBUG: Error type: {type(e)}")
            import traceback
            logger.error(f"DEBUG: Traceback: {traceback.format_exc()}")
            # Continue without the detailed logging
            pass
        
        # Prepare response with all three sections
        try:
            logger.info("DEBUG: Preparing response data...")
            response_data = {
                'success': True,
                'section_1': {
                    'similar_articles': diverse_articles,  # Return only the 5 diverse articles as tiles
                    'total_found': len(diverse_articles)
                },
                'section_2': {
                    'key_facts': analysis_result['analysis'].get('key_facts', []),
                    'opinions': analysis_result['analysis'].get('opinions', []),
                    'biases': analysis_result['analysis'].get('biases', []),
                    'overall_assessment': analysis_result['analysis'].get('overall_assessment', '')
                },
                'section_3': {
                    'genai_score': analysis_result['analysis'].get('genai_analysis', {}).get('genai_probability_score', 0),
                    'genai_reasoning': analysis_result['analysis'].get('genai_analysis', {}).get('reasoning', ''),
                    'genai_telltales': analysis_result['analysis'].get('genai_analysis', {}).get('telltales', [])
                },
                'metadata': {
                    'search_terms': search_terms,
                    'diverse_selection_analysis': diverse_result.get('analysis', ''),
                    'sources_used': ['News API', 'The Guardian', 'The New York Times']
                }
            }
            logger.info("DEBUG: Response data prepared successfully")
            
            # Record request data to DynamoDB if running on AWS
            try:
                # Get user IP address
                user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
                
                # Record to DynamoDB
                record_user_request_to_dynamodb(
                    search_terms=search_terms,
                    user_ip=user_ip,
                    all_articles=articles,
                    top_5_articles=diverse_articles,
                    chatgpt_response=analysis_result['analysis']
                )
            except Exception as e:
                logger.error(f"Error recording to DynamoDB: {e}")
                # Continue without failing the request
            
            return jsonify(response_data)
        except Exception as e:
            logger.error(f"DEBUG: Error preparing response: {e}")
            logger.error(f"DEBUG: Error type: {type(e)}")
            import traceback
            logger.error(f"DEBUG: Traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': f"Error preparing response: {str(e)}"
            }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            'success': False,
            'error': f"An unexpected error occurred: {str(e)}"
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)