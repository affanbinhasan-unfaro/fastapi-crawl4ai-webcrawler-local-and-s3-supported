"""
Custom exceptions for the web scraper application.
"""


class WebScraperException(Exception):
    """Base exception for web scraper application."""
    pass


class ScrapingError(WebScraperException):
    """Raised when scraping fails."""
    def __init__(self, message: str, url: str = None, retry_count: int = 0):
        self.message = message
        self.url = url
        self.retry_count = retry_count
        super().__init__(self.message)


class S3Error(WebScraperException):
    """Raised when S3 operations fail."""
    def __init__(self, message: str, bucket: str = None, key: str = None):
        self.message = message
        self.bucket = bucket
        self.key = key
        super().__init__(self.message)


class ConfigurationError(WebScraperException):
    """Raised when configuration is invalid."""
    pass


class ValidationError(WebScraperException):
    """Raised when data validation fails."""
    pass


class TimeoutError(WebScraperException):
    """Raised when operations timeout."""
    def __init__(self, message: str, timeout_seconds: int = None):
        self.message = message
        self.timeout_seconds = timeout_seconds
        super().__init__(self.message) 