#!/usr/bin/env python3
"""
Test script to verify the web scraper fixes.
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from app.services.scraper import web_scraper
from app.services.data_processor import data_processor
from app.utils.logger import logger


async def test_scraper():
    """Test the scraper with a simple URL."""
    try:
        logger.info("Testing web scraper...")
        
        # Test with a simple website
        test_url = "https://httpbin.org/html"
        company_name = "httpbin"
        
        # Test scraping
        result = await web_scraper.scrape_website(test_url, company_name, max_depth=1)
        
        logger.info(f"Scraping result keys: {list(result.keys())}")
        logger.info(f"Data types found: {list(result['data'].keys())}")
        logger.info(f"Raw HTML pages: {len(result['raw_html'])}")
        logger.info(f"Total pages crawled: {result['metadata']['total_pages_crawled']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Scraper test failed: {e}")
        return False


async def test_data_processor():
    """Test the data processor."""
    try:
        logger.info("Testing data processor...")
        
        # Test with a simple website
        test_url = "https://httpbin.org/html"
        
        # Test processing
        result = await data_processor.process_scraping_request(test_url, max_depth=1)
        
        logger.info(f"Processing result status: {result['status']}")
        if result['status'] == 'success':
            logger.info(f"Storage files: {list(result.get('s3_files', {}).keys())}")
        else:
            logger.error(f"Processing failed: {result.get('error_message')}")
        
        return result['status'] == 'success'
        
    except Exception as e:
        logger.error(f"Data processor test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("Starting web scraper tests...")
    
    # Test scraper
    scraper_ok = await test_scraper()
    
    # Test data processor
    processor_ok = await test_data_processor()
    
    # Summary
    if scraper_ok and processor_ok:
        logger.info("✅ All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 