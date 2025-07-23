# Web Scraper API

A FastAPI-based web scraper application that uses crawl4AI to extract comprehensive data from websites and store it in AWS S3 or local storage with structured file organization.

## Features

- **Comprehensive Data Extraction**: Extracts text content, images, contact information, product data, social media links, and metadata
- **Full Site Crawling**: Recursively crawls all subpages within the same domain up to configurable depth
- **Dual Storage Options**: Stores data in AWS S3 or local storage with identical folder structure
- **Raw HTML Storage**: Preserves complete HTML content for each crawled page
- **Async Processing**: Supports both synchronous and asynchronous scraping with concurrency control
- **Error Handling**: Comprehensive error handling with retry mechanisms
- **API Documentation**: Auto-generated OpenAPI documentation
- **Health Monitoring**: Built-in health check endpoints
- **Configurable**: Environment-based configuration

## Architecture

```
webscraper/
├── app/
│   ├── api/           # FastAPI routes and endpoints
│   ├── core/          # Configuration and exceptions
│   ├── models/        # Pydantic data models
│   ├── services/      # Business logic services
│   └── utils/         # Utility functions and helpers
├── outputs/           # Local storage directory (when S3 disabled)
├── requirements.txt   # Python dependencies
├── env.example        # Environment configuration template
└── README.md         # This file
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
cd webscraper

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
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Core Endpoints

#### POST `/api/v1/scrape`
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
  "total_pages_crawled": 15,
  "processing_time_seconds": 45.2,
  "storage_locations": {
    "text": "s3://bucket/example_corp/text/example_corp_20241201_143022.json",
    "images": "s3://bucket/example_corp/images/example_corp_20241201_143022.json",
    "contact": "s3://bucket/example_corp/contact/example_corp_20241201_143022.json",
    "products": "s3://bucket/example_corp/products/example_corp_20241201_143022.json",
    "social_media": "s3://bucket/example_corp/social_media/example_corp_20241201_143022.json",
    "metadata": "s3://bucket/example_corp/metadata/example_corp_20241201_143022.json",
    "raw_html": "s3://bucket/example_corp/raw_html/example_corp_20241201_143022.json",
    "sitemap": "s3://bucket/example_corp/sitemap/example_corp_20241201_143022.json"
  }
}
```

#### POST `/api/v1/scrape/async`
Start asynchronous scraping (returns immediately).

#### GET `/api/v1/companies/{company_name}/summary`
Get summary of scraped data for a company.

#### GET `/api/v1/companies/{company_name}/files`
List all files for a company.

#### GET `/api/v1/health`
Health check endpoint.

#### GET `/api/v1/storage/info`
Get storage configuration information.

## Data Types Extracted

### Text Content
- Article text and paragraphs
- Page titles and headings
- Content from all crawled pages
- Word counts and confidence scores

### Images
- Image URLs (converted to absolute URLs)
- Alt text and titles
- Dimensions and CSS classes
- Source page information

### Contact Information
- Email addresses (regex pattern matching)
- Phone numbers (multiple format support)
- Physical addresses (street address detection)

### Product Information
- Product names and descriptions
- Pricing information (when available)
- Product cards and listings

### Social Media Links
- Facebook, Twitter, LinkedIn, Instagram, YouTube, TikTok, Pinterest, GitHub
- Platform-specific URLs with link text

### Metadata
- Page titles and meta descriptions
- Keywords and Open Graph tags
- Canonical URLs and language information
- Robots meta tags

### Raw HTML
- Complete HTML content for each crawled page
- Preserved for advanced processing

### Sitemap
- Crawl structure and page relationships
- Data coverage summary
- Link discovery information

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

# Run tests
pytest
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