"""
Unified storage service that switches between S3 and local storage based on configuration.
"""
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.utils.logger import logger

# Import storage services
try:
    from app.services.s3_service import s3_service
    from app.services.local_storage_service import local_storage_service
except ImportError as e:
    logger.warning(f"Could not import storage services: {e}")
    s3_service = None
    local_storage_service = None


class UnifiedStorageService:
    """Unified storage service that switches between S3 and local storage."""
    
    def __init__(self):
        """Initialize the unified storage service."""
        self.use_s3 = settings.save_to_s3
        
        if self.use_s3:
            if s3_service is None:
                raise ImportError("S3 service not available but S3 storage is enabled")
            self.storage_service = s3_service
            logger.info("Using S3 storage service")
        else:
            if local_storage_service is None:
                raise ImportError("Local storage service not available")
            self.storage_service = local_storage_service
            logger.info("Using local storage service")
    
    async def upload_json_data(
        self,
        data: Dict[str, Any],
        company_name: str,
        data_type: str,
        file_name: str
    ) -> str:
        """
        Upload JSON data to storage (S3 or local).
        
        Args:
            data: Data to upload
            company_name: Company name
            data_type: Type of data
            file_name: File name
            
        Returns:
            Storage URL (S3 URL or local file path)
        """
        return await self.storage_service.upload_json_data(
            data, company_name, data_type, file_name
        )
    
    async def upload_error_data(
        self,
        error_data: Dict[str, Any],
        company_name: str
    ) -> str:
        """
        Upload error data to storage.
        
        Args:
            error_data: Error data to upload
            company_name: Company name
            
        Returns:
            Storage URL
        """
        return await self.storage_service.upload_error_data(error_data, company_name)
    
    async def create_company_folders(self, company_name: str) -> None:
        """
        Create folder structure for company.
        
        Args:
            company_name: Company name
        """
        await self.storage_service.create_company_folders(company_name)
    
    async def list_company_files(
        self,
        company_name: str,
        data_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files for a company.
        
        Args:
            company_name: Company name
            data_type: Optional data type filter
            
        Returns:
            List of file information
        """
        return await self.storage_service.list_company_files(company_name, data_type)
    
    async def download_file(self, file_path: str) -> Dict[str, Any]:
        """
        Download and parse JSON file.
        
        Args:
            file_path: File path or S3 key
            
        Returns:
            Parsed JSON data
        """
        return await self.storage_service.download_file(file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file.
        
        Args:
            file_path: File path or S3 key
            
        Returns:
            True if successful
        """
        return await self.storage_service.delete_file(file_path)
    
    def get_storage_type(self) -> str:
        """
        Get the current storage type.
        
        Returns:
            Storage type ('s3' or 'local')
        """
        return "s3" if self.use_s3 else "local"
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage service information.
        
        Returns:
            Storage information
        """
        if self.use_s3:
            return {
                "type": "s3",
                "bucket": settings.s3_bucket_name,
                "region": settings.s3_region,
                "configured": s3_service is not None
            }
        else:
            return {
                "type": "local",
                "base_path": str(local_storage_service.base_path.absolute()),
                "configured": local_storage_service is not None
            }


# Global unified storage service instance
storage_service = UnifiedStorageService() 