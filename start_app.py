#!/usr/bin/env python3
"""
Startup script for the Web Scraper API.
"""
import uvicorn
from app.core.config import settings
from app.utils.logger import logger


def main():
    """Start the web scraper API server."""
    logger.info("Starting Web Scraper API...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,  # Enable auto-reload for development
        log_level=settings.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main() 