"""
Local storage service for file operations with directory structure mirroring S3.
"""
import json
import os
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from app.core.config import settings
from app.core.exceptions import S3Error
from app.utils.logger import logger
from app.utils.helpers import generate_s3_key, retry_async


class LocalStorageService:
    """Service for local file operations with S3-like structure."""
    
    def __init__(self):
        """Initialize the local storage service."""
        self.base_path = Path("outputs")
        self.base_path.mkdir(exist_ok=True)
        logger.info(f"Local storage initialized at: {self.base_path.absolute()}")
    
    async def upload_json_data(
        self,
        data: Dict[str, Any],
        company_name: str,
        data_type: str,
        file_name: str
    ) -> str:
        """
        Upload JSON data to local storage.
        
        Args:
            data: Data to upload
            company_name: Company name
            data_type: Type of data
            file_name: File name
            
        Returns:
            Local file path
        """
        local_path = None
        try:
            # Generate local path (mirroring S3 structure)
            local_path = self._generate_local_path(company_name, data_type, file_name)
            
            # Ensure directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Write to file
            await retry_async(
                self._write_file,
                2,  # max_retries
                1.0,  # delay
                2.0,  # backoff_factor
                local_path,  # file_path argument for _write_file
                json_data  # content argument for _write_file
            )
            
            file_url = f"file://{local_path.absolute()}"
            logger.info(f"Successfully uploaded {data_type} data to {file_url}")
            
            return file_url
            
        except Exception as e:
            error_msg = f"Failed to upload {data_type} data for {company_name}: {e}"
            logger.error(error_msg)
            # Handle case where local_path might not be defined
            local_path_str = str(local_path) if local_path else "undefined"
            raise S3Error(error_msg, str(self.base_path), local_path_str)
    
    async def upload_error_data(
        self,
        error_data: Dict[str, Any],
        company_name: str
    ) -> str:
        """
        Upload error data to local storage.
        
        Args:
            error_data: Error data to upload
            company_name: Company name
            
        Returns:
            Local file path
        """
        file_name = f"{company_name}_crawl_error_{self._get_timestamp()}.json"
        return await self.upload_json_data(
            error_data, company_name, "errors", file_name
        )
    
    async def create_company_folders(self, company_name: str) -> None:
        """
        Create folder structure for company in local storage.
        
        Args:
            company_name: Company name
        """
        folder_types = [
            "text", "images", "contact", "products", 
            "social_media", "metadata", "raw_html", "sitemap", "errors"
        ]
        
        for folder_type in folder_types:
            folder_path = self.base_path / company_name / folder_type
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created folder: {folder_path}")
            except Exception as e:
                logger.warning(f"Could not create folder {folder_path}: {e}")
    
    async def list_company_files(
        self,
        company_name: str,
        data_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files for a company in local storage.
        
        Args:
            company_name: Company name
            data_type: Optional data type filter
            
        Returns:
            List of file information
        """
        try:
            company_path = self.base_path / company_name
            
            if not company_path.exists():
                return []
            
            files = []
            
            if data_type:
                # List files for specific data type
                type_path = company_path / data_type
                if type_path.exists():
                    files.extend(self._scan_directory(type_path, company_name, data_type))
            else:
                # List files for all data types
                for item in company_path.iterdir():
                    if item.is_dir():
                        files.extend(self._scan_directory(item, company_name, item.name))
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files for {company_name}: {e}")
            return []
    
    async def download_file(self, file_path: str) -> Dict[str, Any]:
        """
        Download and parse JSON file from local storage.
        
        Args:
            file_path: Local file path
            
        Returns:
            Parsed JSON data
        """
        try:
            # Remove file:// prefix if present
            if file_path.startswith("file://"):
                file_path = file_path[7:]
            
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            content = await retry_async(
                self._read_file,
                2,  # max_retries
                1.0,  # delay 
                2.0,  # backoff_factor
                path  # file_path argument for _read_file
            )
            
            return json.loads(content)
            
        except Exception as e:
            error_msg = f"Failed to download file {file_path}: {e}"
            logger.error(error_msg)
            raise S3Error(error_msg, str(self.base_path), file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from local storage.
        
        Args:
            file_path: Local file path
            
        Returns:
            True if successful
        """
        try:
            # Remove file:// prefix if present
            if file_path.startswith("file://"):
                file_path = file_path[7:]
            
            path = Path(file_path)
            
            if path.exists():
                await retry_async(
                    self._delete_file_sync,
                    2,  # max_retries
                    1.0,  # delay
                    2.0,  # backoff_factor
                    path  # file_path argument for _delete_file_sync
                )
                logger.info(f"Successfully deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def _generate_local_path(self, company_name: str, data_type: str, file_name: str) -> Path:
        """
        Generate local file path mirroring S3 structure.
        
        Args:
            company_name: Company name
            data_type: Type of data
            file_name: File name
            
        Returns:
            Local file path
        """
        return self.base_path / company_name / data_type / file_name
    
    def _scan_directory(self, directory: Path, company_name: str, data_type: str) -> List[Dict[str, Any]]:
        """
        Scan directory for files and return file information.
        
        Args:
            directory: Directory to scan
            company_name: Company name
            data_type: Data type
            
        Returns:
            List of file information
        """
        files = []
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix == '.json':
                try:
                    stat = file_path.stat()
                    files.append({
                        'key': f"{company_name}/{data_type}/{file_path.name}",
                        'size': stat.st_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'url': f"file://{file_path.absolute()}"
                    })
                except Exception as e:
                    logger.warning(f"Could not get file info for {file_path}: {e}")
        
        return files
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming."""
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    async def _write_file(self, file_path: Path, content: str) -> None:
        """Write content to file (synchronous wrapper for async)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._sync_write_file,
            file_path,
            content
        )
    
    def _sync_write_file(self, file_path: Path, content: str) -> None:
        """Synchronous write file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    async def _read_file(self, file_path: Path) -> str:
        """Read content from file (synchronous wrapper for async)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_read_file,
            file_path
        )
    
    def _sync_read_file(self, file_path: Path) -> str:
        """Synchronous read file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    async def _delete_file_sync(self, file_path: Path) -> None:
        """Delete file (synchronous wrapper for async)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._sync_delete_file,
            file_path
        )
    
    def _sync_delete_file(self, file_path: Path) -> None:
        """Synchronous delete file."""
        file_path.unlink()


# Global local storage service instance
local_storage_service = LocalStorageService() 