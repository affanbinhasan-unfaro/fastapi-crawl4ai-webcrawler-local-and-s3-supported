"""
Simplified Pydantic models for the web scraper API - only /scrape endpoint.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl, validator


class ScrapingRequest(BaseModel):
    """Request model for scraping endpoint."""
    
    url: HttpUrl = Field(..., description="Website URL to scrape")
    company_name: Optional[str] = Field(
        None, 
        description="Company name (auto-extracted if not provided)",
        max_length=100
    )
    max_depth: Optional[int] = Field(
        None,
        description="Maximum crawl depth (overrides config)",
        ge=1,
        le=5
    )
    
    @validator('company_name')
    def validate_company_name(cls, v):
        """Validate company name format."""
        if v is not None:
            # Remove special characters and normalize
            import re
            v = re.sub(r'[^\w\s-]', '', v)
            v = re.sub(r'[-\s]+', '_', v)
            v = v.strip('_')
            if not v:
                raise ValueError("Company name cannot be empty after sanitization")
        return v


class ScrapingResponse(BaseModel):
    """Response model for scraping endpoint."""
    
    status: str = Field(..., description="Processing status (success/error)")
    company_name: str = Field(..., description="Company name")
    url: str = Field(..., description="Source URL")
    timestamp: str = Field(..., description="Processing timestamp")
    
    # Success fields (optional since they may not exist for errors)
    storage_files: Optional[Dict[str, str]] = Field(
        None, 
        description="Storage file URLs by data type"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Scraping metadata"
    )
    
    # Error fields (optional since they only exist for errors)
    error_type: Optional[str] = Field(
        None,
        description="Error type"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message"
    )
    error_file: Optional[str] = Field(
        None,
        description="Storage URL of error file"
    )
    
    @validator('storage_files', pre=True)
    def validate_storage_files(cls, v):
        """Validate storage_files and filter out None values."""
        if v is None:
            return {}
        if isinstance(v, dict):
            # Filter out None values
            return {k: val for k, val in v.items() if val is not None}
        return v 
