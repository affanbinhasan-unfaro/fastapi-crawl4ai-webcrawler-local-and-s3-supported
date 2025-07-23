"""
Utility functions for the web scraper application.
"""
import re
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin
import asyncio
from app.utils.logger import logger


def generate_timestamp() -> str:
    """Generate ISO format timestamp."""
    return datetime.utcnow().isoformat() + "Z"


def sanitize_company_name(company_name: str) -> str:
    """
    Sanitize company name for use in file paths.
    
    Args:
        company_name: Raw company name
        
    Returns:
        Sanitized company name
    """
    # Remove special characters and replace spaces with underscores
    sanitized = re.sub(r'[^\w\s-]', '', company_name)
    sanitized = re.sub(r'[-\s]+', '_', sanitized)
    return sanitized.lower().strip('_')


def extract_domain_from_url(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: Website URL
        
    Returns:
        Domain name
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception as e:
        logger.warning(f"Could not extract domain from URL {url}: {e}")
        return "unknown_domain"


def generate_file_name(company_name: str, data_type: str = "data") -> str:
    """
    Generate standardized file name.
    
    Args:
        company_name: Company name
        data_type: Type of data (data, error, etc.)
        
    Returns:
        Generated file name
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    sanitized_company = sanitize_company_name(company_name)
    sanitized_data_type = sanitize_company_name(data_type)  # Ensure data_type is also sanitized
    
    if data_type == "error":
        return f"{sanitized_company}_crawl_error_{timestamp}.json"
    else:
        return f"{sanitized_company}_{sanitized_data_type}_{timestamp}.json"


def generate_s3_key(company_name: str, data_type: str, file_name: str) -> str:
    """
    Generate S3 key for file storage.
    
    Args:
        company_name: Company name
        data_type: Type of data
        file_name: File name
        
    Returns:
        S3 key path
    """
    sanitized_company = sanitize_company_name(company_name)
    return f"{sanitized_company}/{data_type}/{file_name}"


def is_retriable_error(error: Exception) -> bool:
    """
    Check if an error is retriable.
    
    Args:
        error: Exception to check
        
    Returns:
        True if error is retriable
    """
    retriable_errors = (
        TimeoutError,
        ConnectionError,
        OSError,
    )
    
    # Check for specific error types
    if isinstance(error, retriable_errors):
        return True
    
    # Check for specific error messages
    error_message = str(error).lower()
    retriable_keywords = [
        "timeout",
        "connection",
        "network",
        "temporary",
        "rate limit",
        "too many requests",
        "server error",
        "gateway",
        "bad gateway"
    ]
    
    return any(keyword in error_message for keyword in retriable_keywords)


async def retry_async(
    func,
    max_retries: int = 2,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs
) -> Any:
    """
    Retry async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        delay: Initial delay in seconds
        backoff_factor: Backoff multiplier
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries or not is_retriable_error(e):
                raise e
            
            logger.warning(
                f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                f"Retrying in {delay} seconds..."
            )
            
            await asyncio.sleep(delay)
            delay *= backoff_factor
    
    raise last_exception


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid
    """
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False


def extract_company_name_from_url(url: str) -> str:
    """
    Extract company name from URL domain.
    
    Args:
        url: Website URL
        
    Returns:
        Extracted company name
    """
    domain = extract_domain_from_url(url)
    
    # Remove common TLDs and subdomains
    parts = domain.split('.')
    if len(parts) >= 2:
        # Remove www and other common subdomains
        if parts[0] in ['www', 'web', 'app', 'api']:
            company_part = parts[1]
        else:
            company_part = parts[0]
        
        # Convert to title case and replace hyphens/underscores
        company_name = company_part.replace('-', ' ').replace('_', ' ').title()
        return company_name
    
    return domain.title()


def create_metadata(
    source_url: str,
    company_name: str,
    crawl_depth: int,
    total_pages: int,
    processing_time: float
) -> Dict[str, Any]:
    """
    Create metadata for scraping results.
    
    Args:
        source_url: Source URL
        company_name: Company name
        crawl_depth: Crawl depth used
        total_pages: Total pages crawled
        processing_time: Processing time in seconds
        
    Returns:
        Metadata dictionary
    """
    return {
        "scraping_timestamp": generate_timestamp(),
        "source_url": source_url,
        "company_name": company_name,
        "extraction_method": "crawl4AI_HTTP_BeautifulSoup",
        "crawl_depth": crawl_depth,
        "total_pages_crawled": total_pages,
        "processing_time_seconds": round(processing_time, 2)
    }


def create_error_response(
    error: Exception,
    company_name: str,
    url: str,
    retry_count: int = 0
) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error: Exception that occurred
        company_name: Company name
        url: Source URL
        retry_count: Number of retries attempted
        
    Returns:
        Error response dictionary
    """
    return {
        "status": "error",
        "company_name": company_name,
        "url": url,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "retry_count": retry_count,
        "timestamp": generate_timestamp(),
        "s3_error_file": None  # Will be set by S3 service
    } 