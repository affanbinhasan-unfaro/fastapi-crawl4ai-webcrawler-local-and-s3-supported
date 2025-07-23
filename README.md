# Web Scraper API

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
  - [Prerequisites](#1-prerequisites)
  - [Installation](#2-installation)
  - [Configuration](#3-configuration)
  - [Run the Application](#4-run-the-application)
- [API Endpoints](#api-endpoints)
  - [Core Endpoints](#core-endpoints)
  - [Data Types Extracted](#data-types-extracted)
- [Storage Structure](#storage-structure)
- [Error Handling](#error-handling)
- [Configuration Options](#configuration-options)
  - [Crawl Settings](#crawl-settings)
  - [Storage Settings](#storage-settings)
  - [API Settings](#api-settings)
  - [Logging](#logging)
- [Crawling Behavior](#crawling-behavior)
- [Development](#development)
  - [Running Tests](#running-tests)
  - [Test Suite Structure](#test-suite-structure)
  - [Code Style](#code-style)
- [Deployment](#deployment)
- [License](#license)

A FastAPI-based web scraper application that uses crawl4AI to extract comprehensive data from websites and store it in AWS S3 or local storage with structured file organization.

## Features

- **Comprehensive Data Extraction**: Extracts text content, images, contact information, product data, social media links, and metadata
- **Full Site Crawling**: Recursively crawls all subpages within the same domain up to configurable depth
- **Dual Storage Options**: Stores data in AWS S3 or local storage with identical folder structure
- **Raw HTML Storage**: Preserves complete HTML content for each crawled page
- **Async Processing**: Supports both synchronous and asynchronous scraping with concurrency control
- **Error Handling**: Comprehensive error handling with retry mechanisms
- **API Documentation**: Auto-generated OpenAPI documentation
- **Configurable**: Environment-based configuration

## Architecture

```
webscraper/
├── app/
│   ├── api/           # FastAPI routes and endpoints
│   │   └── routes.py
│   ├── core/          # Configuration and exceptions
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── models/        # Pydantic data models
│   │   └── schemas.py
│   ├── services/      # Business logic services
│   │   ├── scraper.py
│   │   ├── data_processor.py
│   │   ├── storage_service.py
│   │   ├── local_storage_service.py
│   │   └── s3_service.py
│   └── utils/         # Utility functions and helpers
│       ├── helpers.py
│       └── logger.py
├── outputs/           # Local storage directory (when S3 disabled)
├── requirements.txt   # Python dependencies
├── env.example        # Environment configuration template
├── start_app.py       # API server startup script
├── tests/             # Test suite (see below)
└── README.md          # This file
```

### Test Suite Structure

```
tests/
├── __init__.py
├── conftest.py           # Pytest configuration and fixtures
├── README.md             # Test suite documentation
├── run_tests.py          # Test runner script
│
├── unit/                 # Unit tests (individual components)
│   ├── __init__.py
│   ├── test_contact_extraction.py
│   ├── test_crawler.py
│   ├── test_fixes.py
│   └── test_storage.py
│
├── integration/          # Integration tests (end-to-end workflows)
│   ├── __init__.py
│   ├── test_api_integration.py
│   ├── test_contact_with_real_website.py
│   ├── test_scraper_integration.py
│   ├── test_simplified_api.py
│   └── test_updated_scraper.py
│
├── debug/                # Debug scripts (diagnostic tools)
│   ├── __init__.py
│   ├── debug_contact_simple.py
│   ├── debug_contact_step_by_step.py
│   ├── debug_crawler.py
│   ├── debug_links.py
│   └── debug_storage_issue.py
│
└── api/                  # API-specific tests (future)
    └── __init__.py
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- AWS S3 bucket (optional, for S3 storage)
- AWS credentials (optional, for S3 storage)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy the environment template and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Crawl Settings
MAX_CRAWL_DEPTH=2  # Maximum crawl depth for recursive crawling
CRAWL_TIMEOUT=300  # Crawl timeout in seconds (per page, for crawl4ai)
MAX_CONCURRENT_REQUESTS=10

# Storage Configuration
SAVE_TO_S3=false  # Set to true for S3 storage, false for local storage
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FILE=webscraper.log
```

### 4. Run the Application

```bash
# Start the API server
python start_app.py

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

## API Endpoint

### POST `/api/v1/scrape`
Scrape a website and store data in S3 or local storage.

**Request Body:**
```json
{
  "url": "https://example.com",
  "company_name": "Example Corp",  // Optional
  "max_depth": 2                   // Optional
}
```

**Response:**
```json
{
  "status": "success",
  "company_name": "Example Corp",
  "url": "https://example.com",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "storage_files": {
    "text": "file:///outputs/example_corp/text/example_corp_text_20240101_120000.json",
    "images": "file:///outputs/example_corp/images/example_corp_images_20240101_120000.json",
    "contact": "file:///outputs/example_corp/contact/example_corp_contact_20240101_120000.json"
  },
  "metadata": {
    "extraction_method": "crawl4AI_HTTP_BeautifulSoup",
    "total_pages_crawled": 5,
    "processing_time_seconds": 12.34
  }
}
```

## Data Types Extracted

- **Text Content**: Article text, paragraphs, titles, headings
- **Images**: Image URLs, alt text, dimensions
- **Contact Information**: Email addresses, phone numbers
- **Product Information**: Product names, descriptions, prices (when available)
- **Social Media Links**: Facebook, Twitter, LinkedIn, Instagram, etc.
- **Metadata**: Page titles, meta descriptions, Open Graph tags
- **Raw HTML**: Complete HTML content for each crawled page
- **Sitemap**: Crawl structure and page relationships

## Storage Structure

Both S3 and local storage use the same folder structure:

```
{storage_root}/
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

## Error Handling

The application includes comprehensive error handling:

- **Retry Mechanism**: Automatic retries for network errors (max 2 retries)
- **Error Logging**: Detailed error information stored in storage
- **Partial Success**: Continues processing even if some data types fail
- **Graceful Degradation**: Returns partial results when possible

## Configuration Options

### Crawl Settings
- `MAX_CRAWL_DEPTH`: Maximum crawl depth for recursive crawling (default: 2)
- `CRAWL_TIMEOUT`: Timeout for crawling operations in seconds (default: 300)
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent requests (default: 10)

### Storage Settings
- `SAVE_TO_S3`: Flag to enable S3 storage (false = local storage, true = S3 storage)
- `S3_BUCKET_NAME`: Target S3 bucket name (required when SAVE_TO_S3=true)
- `S3_REGION`: AWS region for S3 bucket (required when SAVE_TO_S3=true)
- `AWS_ACCESS_KEY_ID`: AWS access key (optional, uses default credential chain)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (optional, uses default credential chain)

### API Settings
- `API_HOST`: Host to bind the API server (default: 0.0.0.0)
- `API_PORT`: Port for the API server (default: 8000)
- `API_WORKERS`: Number of worker processes (default: 4)

### Logging
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `LOG_FILE`: Log file path (default: webscraper.log)

## Crawling Behavior

The scraper uses crawl4ai for comprehensive website crawling:

1. **Domain Restriction**: Only crawls pages within the same domain as the starting URL
2. **Depth Control**: Respects the configured maximum crawl depth
3. **Concurrency**: Uses configurable concurrent requests with semaphore control
4. **Link Discovery**: Extracts and follows all internal links found on each page
5. **URL Normalization**: Normalizes URLs to avoid duplicate crawling
6. **Smart Content Extraction**: Uses crawl4ai's magic mode for enhanced content extraction

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/
```

### Test Suite Structure

```
tests/
├── __init__.py
├── conftest.py           # Pytest configuration and fixtures
├── README.md             # Test suite documentation
├── run_tests.py          # Test runner script
│
├── unit/                 # Unit tests (individual components)
│   ├── __init__.py
│   ├── test_contact_extraction.py
│   ├── test_crawler.py
│   ├── test_fixes.py
│   └── test_storage.py
│
├── integration/          # Integration tests (end-to-end workflows)
│   ├── __init__.py
│   ├── test_api_integration.py
│   ├── test_contact_with_real_website.py
│   ├── test_scraper_integration.py
│   ├── test_simplified_api.py
│   └── test_updated_scraper.py
│
├── debug/                # Debug scripts (diagnostic tools)
│   ├── __init__.py
│   ├── debug_contact_simple.py
│   ├── debug_contact_step_by_step.py
│   ├── debug_crawler.py
│   ├── debug_links.py
│   └── debug_storage_issue.py
│
└── api/                  # API-specific tests (future)
    └── __init__.py
```

### Code Style

The project follows Python best practices with:
- Type hints throughout
- Comprehensive error handling
- Structured logging
- Async/await patterns
- Clean separation of concerns

## Deployment

The application is designed for AWS deployment with:
- Environment-based configuration
- S3 integration for scalable storage
- Health check endpoints for load balancers
- Structured logging for monitoring

## License

[Add your license information here] 