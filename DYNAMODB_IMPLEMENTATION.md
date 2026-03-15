# DynamoDB Integration Implementation

## Overview
Added functionality to record user request data to DynamoDB when the application is running on AWS.

## Changes Made

### 1. Updated `config.py`
- Added `import os` at the top
- Added DynamoDB configuration variables:
  - `DYNAMODB_TABLE_NAME = "news_filter_requests"`
  - `DYNAMODB_REGION = "us-east-1"`
  - `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from environment variables

### 2. Updated `requirements.txt`
- Added `boto3>=1.26.0` for AWS SDK functionality

### 3. Updated `app.py`
- Added imports: `json` and `datetime`
- Added config imports for DynamoDB settings
- Added `is_running_on_aws()` function to detect AWS environment
- Added `record_user_request_to_dynamodb()` function that records:
  1. Search terms (JSON string)
  2. User IP address
  3. All articles found (JSON)
  4. Top 3 articles (JSON)
  5. Complete ChatGPT response
- Modified `analyze_article_endpoint()` to call the recording function after successful analysis

## Key Features

### AWS Detection
The function only runs when deployed on AWS by checking for:
- `AWS_LAMBDA_FUNCTION_NAME` environment variable
- `ECS_CONTAINER_METADATA_URI` environment variable

### Data Storage
Each request is stored with:
- `request_id`: Timestamp as unique identifier
- `timestamp`: ISO format timestamp
- `search_terms`: JSON string of search terms used
- `user_ip_address`: Client IP address (with X-Forwarded-For support)
- `all_articles`: JSON string of all fetched articles
- `top_3_articles`: JSON string of the 3 selected diverse articles
- `chatgpt_response`: JSON string of the complete analysis response

### Error Handling
- DynamoDB recording failures are logged but don't break the main functionality
- Local development skips recording entirely

## Deployment Requirements

### Environment Variables
Set these in your AWS environment:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### DynamoDB Table
Create a DynamoDB table named `news_filter_requests` with:
- Primary key: `request_id` (String)
- Region: `us-east-1` (or modify `DYNAMODB_REGION` in config)

### IAM Permissions
Ensure your AWS role has permissions for:
- `dynamodb:PutItem` on the `news_filter_requests` table

## Usage
The recording happens automatically on successful article analysis when running on AWS. No additional API calls or configuration needed.
