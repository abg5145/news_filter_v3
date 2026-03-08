import os
import logging
logging.basicConfig(level=logging.DEBUG)
from flask import Flask, render_template, request, jsonify
from api_calls.generate_search_terms import generate_search_terms
from api_calls.select_diverse_articles import select_diverse_articles
from api_calls.analyze_article import analyze_article
from utils.article_fetcher import fetch_articles_from_sources

app = Flask(__name__)

print("Flask app created successfully")
print("Environment variables:", {k: v for k, v in os.environ.items() if 'API' in k or 'KEY' in k})

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
        
        print("Step 1: Generating search terms...")
        # Step 1: Generate search terms using ChatGPT (cheaper model)
        search_result = generate_search_terms(article_text)
        if not search_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to generate search terms: {search_result['error']}"
            }), 500
        
        search_terms = search_result['search_terms']
        print(f"Generated search terms: {search_terms}")
        
        print("Step 2: Fetching articles from multiple sources...")
        # Step 2: Fetch articles from at least 3 news sources
        articles = fetch_articles_from_sources(search_terms, ['news_api', 'guardian', 'nytimes'])
        print(f"Fetched {len(articles)} articles")
        
        if len(articles) < 3:
            return jsonify({
                'success': False,
                'error': f"Could not fetch enough articles. Only found {len(articles)} articles."
            }), 500
        
        print("Step 3: Selecting diverse articles...")
        # Step 3: Select top 3 articles with differing viewpoints using ChatGPT (cheaper model)
        diverse_result = select_diverse_articles(articles, article_text)
        if not diverse_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to select diverse articles: {diverse_result['error']}"
            }), 500
        
        selected_indices = [article['article_index'] - 1 for article in diverse_result['selected_articles']]
        diverse_articles = [articles[i] for i in selected_indices if i < len(articles)]
        print(f"Selected {len(diverse_articles)} diverse articles")
        
        print("Step 4: Performing comprehensive analysis...")
        # Step 4: Analyze original article with diverse articles using ChatGPT (advanced model)
        analysis_result = analyze_article(article_text, diverse_articles)
        if not analysis_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to analyze article: {analysis_result['error']}"
            }), 500
        
        print("Analysis complete!")
        
        # Prepare response with all three sections
        response_data = {
            'success': True,
            'section_1': {
                'similar_articles': diverse_articles,  # Return only the 3 diverse articles as tiles
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
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
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