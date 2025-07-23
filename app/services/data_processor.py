"""
Simplified data processing service for organizing scraped data.
"""
from typing import Dict, Any, Optional
from app.utils.logger import logger
from app.utils.helpers import (
    generate_file_name,
    extract_company_name_from_url,
    validate_url
)
from app.services.storage_service import storage_service
from app.services.scraper import web_scraper


class DataProcessor:
    """Simplified service for processing and organizing scraped data."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.storage_service = storage_service
        self.scraper = web_scraper
    
    async def process_scraping_request(
        self,
        url: str,
        company_name: Optional[str] = None,
        max_depth: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a complete scraping request.
        
        Args:
            url: Website URL to scrape
            company_name: Optional company name (auto-extracted if not provided)
            max_depth: Optional max crawl depth
            
        Returns:
            Processing result with storage file locations
        """
        
        try:
            # Validate URL
            if not validate_url(url):
                raise ValueError(f"Invalid URL format: {url}")
            
            # Extract company name if not provided
            if not company_name:
                company_name = extract_company_name_from_url(url)
                logger.info(f"Auto-extracted company name: {company_name}")
            
            # Create company folder structure
            await self.storage_service.create_company_folders(company_name)
            
            # Scrape the website
            scraped_data = await self.scraper.scrape_website(url, company_name, max_depth)
            
            # Process and upload data to storage
            storage_files = await self._upload_scraped_data(scraped_data, company_name)
            
            # Filter out None values from storage_files
            filtered_storage_files = {
                key: value for key, value in storage_files.items() 
                if value is not None
            }
            
            # Create success response
            return {
                'status': 'success',
                'company_name': company_name,
                'url': url,
                'storage_files': filtered_storage_files,
                'metadata': scraped_data['metadata'],
                'timestamp': scraped_data['metadata']['scraping_timestamp']
            }
            
        except Exception as e:
            logger.error(f"Failed to process scraping request for {url}: {e}")
            
            # Create error response
            error_response = {
                'status': 'error',
                'company_name': company_name or extract_company_name_from_url(url),
                'url': url,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'timestamp': self._get_timestamp()
            }
            
            # Upload error to storage
            try:
                error_file_url = await self.storage_service.upload_error_data(
                    error_response, company_name or extract_company_name_from_url(url)
                )
                error_response['error_file'] = error_file_url
            except Exception as upload_error:
                logger.error(f"Failed to upload error data: {upload_error}")
                error_response['error_file'] = None
            
            return error_response
    
    async def _upload_scraped_data(
        self,
        scraped_data: Dict[str, Any],
        company_name: str
    ) -> Dict[str, str]:
        """
        Upload scraped data to storage organized by data type.
        
        Args:
            scraped_data: Complete scraped data
            company_name: Company name
            
        Returns:
            Dictionary mapping data types to storage URLs
        """
        storage_files = {}
        
        # Define data types and their corresponding data
        data_types = {
            'text': scraped_data['data']['text'],
            'images': scraped_data['data']['images'],
            'contact': scraped_data['data']['contact'],
            'products': scraped_data['data']['products'],
            'social_media': scraped_data['data']['social_media'],
            'metadata': scraped_data['data']['metadata'],
            'raw_html': scraped_data['raw_html'],
            'sitemap': scraped_data['sitemap']
        }
        
        # Upload each data type
        for data_type, data in data_types.items():
            try:
                if data:  # Only upload if data exists
                    file_name = generate_file_name(company_name, data_type)
                    
                    # Create comprehensive data structure for this type
                    upload_data = {
                        'metadata': scraped_data['metadata'],
                        'data': data,
                        'data_type': data_type,
                        'company_name': company_name,
                        'extraction_summary': self._create_data_summary(data, data_type)
                    }
                    
                    # Upload to storage
                    storage_url = await self.storage_service.upload_json_data(
                        upload_data, company_name, data_type, file_name
                    )
                    
                    storage_files[data_type] = storage_url
                    logger.info(f"Uploaded {data_type} data: {storage_url}")
                else:
                    logger.info(f"No {data_type} data to upload")
                    
            except Exception as e:
                logger.error(f"Failed to upload {data_type} data for {company_name}: {e}")
        
        return storage_files
    
    def _create_data_summary(self, data: Any, data_type: str) -> Dict[str, Any]:
        """
        Create summary of data content for better organization.
        
        Args:
            data: Data to summarize
            data_type: Type of data
            
        Returns:
            Data summary
        """
        try:
            summary = {
                'data_type': data_type,
                'total_items': 0,
                'has_content': bool(data)
            }
            
            # Type-specific summaries
            if data_type == 'text' and isinstance(data, list):
                summary.update({
                    'total_items': len(data),
                    'content_types': list(set(item.get('extraction_method', 'unknown') for item in data))
                })
            elif data_type == 'images' and isinstance(data, list):
                summary.update({
                    'total_items': len(data),
                    'unique_domains': len(set(item.get('page_url', '') for item in data))
                })
            elif data_type == 'contact' and isinstance(data, list):
                contact_types = {}
                for item in data:
                    contact_type = item.get('type', 'unknown')
                    contact_types[contact_type] = contact_types.get(contact_type, 0) + 1
                summary.update({
                    'total_items': len(data),
                    'contact_types': contact_types
                })
            elif data_type == 'raw_html' and isinstance(data, dict):
                summary.update({
                    'total_items': len(data),
                    'total_html_size': sum(len(html) for html in data.values())
                })
            elif data_type == 'sitemap' and isinstance(data, dict):
                crawl_structure = data.get('crawl_structure', {})
                coverage_summary = data.get('coverage_summary', {})
                summary.update({
                    'total_items': len(crawl_structure),
                    'coverage_summary': coverage_summary
                })
            elif isinstance(data, list):
                summary['total_items'] = len(data)
            elif isinstance(data, dict):
                summary['total_items'] = len(data)
            
            return summary
            
        except Exception as e:
            logger.warning(f"Failed to create summary for {data_type}: {e}")
            return {
                'data_type': data_type,
                'error': str(e),
                'has_content': bool(data)
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


# Global data processor instance
data_processor = DataProcessor() 