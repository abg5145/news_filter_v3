# UPDATE 3/1 News Filter - Unbiased Article Analysis

A web application that analyzes news articles for bias, facts, opinions, and AI-generated content by comparing them with articles from multiple news sources.

## Features

- **Multi-source Article Comparison**: Fetches similar articles from News API, The Guardian, and The New York Times
- **Bias Detection**: Identifies various types of biases in news articles
- **Fact vs Opinion Analysis**: Separates factual statements from subjective opinions
- **AI Generation Detection**: Scores articles on likelihood of being AI-generated (0-100)
- **Diverse Perspective Selection**: Selects articles with different viewpoints for comprehensive analysis

## Architecture

The application follows a modular design as specified:

### Backend Structure

```
news_filter_v2/
├── config.py                 # All API keys and configuration
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── api_calls/              # ChatGPT API functions
│   ├── generate_search_terms.py    # Step 1: Generate search terms (cheap model)
│   ├── select_diverse_articles.py  # Step 2: Select diverse articles (cheap model)
│   └── analyze_article.py          # Step 3: Comprehensive analysis (advanced model)
├── utils/                  # Utility functions
│   ├── openai_client.py    # Common ChatGPT API abstraction
│   └── article_fetcher.py  # Main article fetching function
├── news_sources/           # Individual news source functions
│   ├── news_api.py         # News API integration
│   ├── guardian_api.py     # The Guardian API integration
│   └── nytimes_api.py     # New York Times API integration
└── templates/              # Frontend templates
    └── index.html
```

### API Usage

1. **First Call (GPT-3.5-turbo)**: Generates search terms from article text
2. **Second Call (GPT-3.5-turbo)**: Selects 3 diverse articles from fetched results
3. **Third Call (GPT-4o)**: Performs comprehensive analysis including AI detection

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys**:
   Edit `config.py` and add your API keys:
   ```python
   OPENAI_API_KEY = "your_openai_api_key_here"
   NEWS_API_KEY = "your_news_api_key_here"
   GUARDIAN_API_KEY = "your_guardian_api_key_here"
   NYTIMES_API_KEY = "your_nytimes_api_key_here"
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## Required API Keys

1. **OpenAI API Key**: For ChatGPT calls
2. **News API Key**: For general news articles
3. **Guardian API Key**: For The Guardian articles
4. **New York Times API Key**: For NY Times articles

## Usage

1. Paste the text of a news article into the input field
2. Click "Analyze Article"
3. View the three response sections:
   - **Section 1**: Similar articles from other sources as tiles
   - **Section 2**: Analysis of facts, opinions, and biases
   - **Section 3**: AI generation probability score (0-100)

## Design Requirements Met

✅ All API keys in a single file (`config.py`)
✅ Each ChatGPT API call in a separate function
✅ Common abstract function for ChatGPT calls (`OpenAIClient.call_chatgpt`)
✅ Single function for fetching articles with separate source functions
✅ Backend in Python
✅ First and second ChatGPT calls use cheaper models (GPT-3.5-turbo)
✅ Third ChatGPT call uses advanced model (GPT-4o)

## Technical Details

- **Framework**: Flask for web backend
- **Frontend**: HTML5, Tailwind CSS, vanilla JavaScript
- **API Integration**: RESTful APIs for news sources
- **Error Handling**: Comprehensive error handling and user feedback
- **Responsive Design**: Mobile-friendly interface

## License

This project is for educational and demonstration purposes.
