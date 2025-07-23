"""
Simplified FastAPI routes for the web scraper API - only /scrape endpoint.
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ScrapingRequest, ScrapingResponse
from app.services.data_processor import data_processor
from app.utils.logger import logger

# Create router
router = APIRouter()


@router.post("/scrape", response_model=ScrapingResponse)
async def scrape_website(request: ScrapingRequest) -> ScrapingResponse:
    """
    Scrape a website and store data in storage.
    
    Args:
        request: Scraping request with URL and optional parameters
        
    Returns:
        Scraping response with status and storage file locations
    """
    try:
        logger.info(f"Received scraping request for: {request.url}")
        
        # Process the scraping request
        result = await data_processor.process_scraping_request(
            url=str(request.url),
            company_name=request.company_name,
            max_depth=request.max_depth
        )
        
        # Ensure storage_files is not None
        storage_files = result.get('storage_files', {})
        if storage_files is None:
            storage_files = {}
        
        # Convert to response model
        response = ScrapingResponse(
            status=result['status'],
            company_name=result['company_name'],
            url=result['url'],
            timestamp=result['timestamp'],
            storage_files=storage_files,
            metadata=result.get('metadata'),
            error_type=result.get('error_type'),
            error_message=result.get('error_message'),
            error_file=result.get('error_file')
        )
        
        if result['status'] == 'success':
            logger.info(f"Successfully scraped {request.url}")
        else:
            logger.error(f"Failed to scrape {request.url}: {result.get('error_message')}")
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in scrape endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 