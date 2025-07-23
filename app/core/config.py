"""
Configuration management for the web scraper application.
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Crawl Settings
    max_crawl_depth: int = Field(default=2, description="Maximum crawl depth for recursive crawling")
    crawl_timeout: int = Field(default=300, description="Crawl timeout in seconds (per page, for crawl4ai)")
    max_concurrent_requests: int = Field(default=10, description="Maximum concurrent requests")
    
    # S3 Configuration
    save_to_s3: bool = Field(default=False, description="Flag to enable S3 storage (False = local storage)")
    s3_bucket_name: str = Field(default="webscraper-data", description="S3 bucket name")
    s3_region: str = Field(default="us-east-1", description="S3 region")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_file: str = Field(default="webscraper.log", description="Log file path")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings() 