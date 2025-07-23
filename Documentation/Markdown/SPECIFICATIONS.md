# Web Scraper Application Specifications

## Overview
A FastAPI-based web scraper application that uses crawl4AI to extract comprehensive data from websites and store it in S3 with structured file organization.

## Core Components

### 1. API Endpoint
- **Method**: POST
- **Path**: `/scrape`
- **Request Body**:
  ```json
  {
    "url": "https://example.com",
    "company_name": "optional_company_name",
    "max_depth": 2
  }
  ```
- **Response**: JSON with scraping status and S3 file locations

### 2. Data Extraction Types
- **Text Content**: Articles, descriptions, paragraphs
- **Images**: Image URLs, alt text, dimensions
- **Contact Information**: Emails, phone numbers, addresses
- **Product Information**: Product names, prices, descriptions
- **Social Media Links**: Facebook, Twitter, LinkedIn, etc.
- **Metadata**: Titles, descriptions, keywords, Open Graph tags
- **Raw HTML**: Complete HTML content for each page
- **Sitemap**: Crawl structure and data coverage

### 3. S3 File Structure
```
s3://bucket-name/
├── {company_name}/
│   ├── text/
│   │   └── {company_name}_{timestamp}.json
│   ├── images/
│   │   └── {company_name}_{timestamp}.json
│   ├── contact/
│   │   └── {company_name}_{timestamp}.json
│   ├── products/
│   │   └── {company_name}_{timestamp}.json
│   ├── social_media/
│   │   └── {company_name}_{timestamp}.json
│   ├── metadata/
│   │   └── {company_name}_{timestamp}.json
│   ├── raw_html/
│   │   └── {company_name}_{timestamp}.json
│   ├── sitemap/
│   │   └── {company_name}_{timestamp}.json
│   └── errors/
│       └── {company_name}_crawl_error_{timestamp}.json
```

### 4. JSON Output Structure
```json
{
  "metadata": {
    "scraping_timestamp": "2024-12-01T14:30:22Z",
    "source_url": "https://example.com",
    "company_name": "Example Corp",
    "extraction_method": "crawl4AI",
    "crawl_depth": 2,
    "total_pages_crawled": 15,
    "processing_time_seconds": 45.2
  },
  "data": {
    "text": [
      {
        "content": "Extracted text content",
        "page_url": "https://example.com/page1",
        "confidence_score": 0.95,
        "extraction_method": "crawl4AI"
      }
    ],
    "images": [
      {
        "url": "https://example.com/image.jpg",
        "alt_text": "Image description",
        "dimensions": {"width": 800, "height": 600},
        "page_url": "https://example.com/page1",
        "confidence_score": 0.98
      }
    ],
    "contact": [
      {
        "type": "email",
        "value": "contact@example.com",
        "page_url": "https://example.com/contact",
        "confidence_score": 0.99
      }
    ],
    "products": [...],
    "social_media": [...],
    "metadata": {...}
  },
  "raw_html": {
    "https://example.com": "<html>...</html>",
    "https://example.com/page1": "<html>...</html>"
  },
  "sitemap": {
    "crawl_structure": {
      "https://example.com": {
        "depth": 0,
        "links_found": ["/about", "/contact"],
        "data_extracted": ["text", "images", "contact"]
      }
    },
    "coverage_summary": {
      "total_pages": 15,
      "pages_with_text": 12,
      "pages_with_images": 8,
      "pages_with_contact": 3
    }
  }
}
```

### 5. Error Handling
- **Retry Mechanism**: Max 2 retries for retriable errors (network timeouts, 5xx errors)
- **Error Logging**: Detailed error JSON files in S3 error folder
- **Partial Success**: Continue processing even if some data types fail
- **Error Response Structure**:
  ```json
  {
    "status": "error",
    "company_name": "Example Corp",
    "url": "https://example.com",
    "error_type": "network_timeout",
    "error_message": "Connection timeout after 30 seconds",
    "retry_count": 2,
    "timestamp": "2024-12-01T14:30:22Z",
    "s3_error_file": "s3://bucket/example_corp/errors/example_corp_crawl_error_20241201_143022.json"
  }
  ```

### 6. Environment Configuration
```env
# Crawl Settings
MAX_CRAWL_DEPTH=2
CRAWL_TIMEOUT=300
MAX_CONCURRENT_REQUESTS=10

# Storage Configuration
SAVE_TO_S3=false  # Set to true for S3 storage, false for local storage
S3_BUCKET_NAME=webscraper-data
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FILE=webscraper.log
```

### 7. Performance Requirements
- **Concurrent Processing**: Utilize async/await for I/O operations
- **Memory Management**: Stream large responses to avoid memory issues
- **Timeout Handling**: Configurable timeouts for different operations
- **Rate Limiting**: Respect robots.txt and implement polite delays

### 8. Dependencies
- FastAPI (API framework)
- crawl4AI (Web scraping)
- boto3 (AWS S3 integration)
- pydantic (Data validation)
- asyncio (Async processing)
- aiofiles (Async file operations)
- python-dotenv (Environment management)

### 9. Project Structure
```
webscraper/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   └── exceptions.py    # Custom exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scraper.py       # crawl4AI integration
│   │   ├── s3_service.py    # S3 operations
│   │   └── data_processor.py # Data processing logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py       # Utility functions
│       └── logger.py        # Logging configuration
├── requirements.txt
├── .env.example
├── README.md
└── SPECIFICATIONS.md
```

## Implementation Phases

### Phase 1: Core Setup
1. Project structure and dependencies
2. Configuration management
3. Basic FastAPI setup

### Phase 2: Core Services
1. S3 service implementation
2. crawl4AI integration
3. Data processing logic

### Phase 3: API Development
1. API endpoint implementation
2. Request/response models
3. Error handling

### Phase 4: Testing & Optimization
1. Unit tests
2. Integration tests
3. Performance optimization

### Phase 5: Documentation & Deployment
1. API documentation
2. Deployment configuration
3. Monitoring setup 