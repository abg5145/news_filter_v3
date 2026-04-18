import os
# Add your API keys here

OPENAI_API_KEY = "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"
NEWS_API_KEY = "68487c2992f94941a8411595b3df9742"
GUARDIAN_API_KEY = "71011091-f837-4627-9ae6-78851c554fbc"
NYTIMES_API_KEY = "rGB0wXngW7FCXk7I6Z7JRA4AqvRGzAu770S2uMdC2g2Bn9Mw"
EVENT_REGISTRY_API_KEY = "fb7997c7-bb07-4870-9e0e-e118d86e2e64"

# API Configuration
OPENAI_BASE_URL = "https://api.openai.com/v1"
NEWS_API_BASE_URL = "https://newsapi.org/v2"
GUARDIAN_BASE_URL = "https://content.guardianapis.com"
NYTIMES_BASE_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
EVENT_REGISTRY_BASE_URL = "https://eventregistry.org/api/v1"

# Model Configuration
CHEAP_MODEL = "gpt-3.5-turbo"
ADVANCED_MODEL = "gpt-4o"  # Using GPT-4o as equivalent to model 5.2

# DynamoDB Configuration
DYNAMODB_TABLE_NAME = "news_filter_requests"
DYNAMODB_REGION = "us-east-1"  # Adjust as needed
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
