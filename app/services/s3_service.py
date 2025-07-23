"""
S3 service for handling file operations with AWS S3.
"""
import json
import asyncio
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.config import settings
from app.core.exceptions import S3Error
from app.utils.logger import logger
from app.utils.helpers import generate_s3_key, retry_async


class S3Service:
    """Service for S3 operations."""
    
    def __init__(self):
        """Initialize S3 client."""
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.s3_region
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.warning("AWS credentials not found. Using default credential chain.")
            self.s3_client = boto3.client('s3', region_name=self.region)
    
    async def upload_json_data(
        self,
        data: Dict[str, Any],
        company_name: str,
        data_type: str,
        file_name: str
    ) -> str:
        """
        Upload JSON data to S3.
        
        Args:
            data: Data to upload
            company_name: Company name
            data_type: Type of data
            file_name: File name
            
        Returns:
            S3 URL of uploaded file
            
        Raises:
            S3Error: If upload fails
        """
        try:
            # Generate S3 key
            s3_key = generate_s3_key(company_name, data_type, file_name)
            
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Upload to S3
            await retry_async(
                self._upload_file,
                json_data.encode('utf-8'),
                s3_key,
                'application/json'
            )
            
            s3_url = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(f"Successfully uploaded {data_type} data to {s3_url}")
            
            return s3_url
            
        except Exception as e:
            error_msg = f"Failed to upload {data_type} data for {company_name}: {e}"
            logger.error(error_msg)
            raise S3Error(error_msg, self.bucket_name, s3_key)
    
    async def upload_error_data(
        self,
        error_data: Dict[str, Any],
        company_name: str
    ) -> str:
        """
        Upload error data to S3.
        
        Args:
            error_data: Error data to upload
            company_name: Company name
            
        Returns:
            S3 URL of uploaded error file
        """
        file_name = f"{company_name}_crawl_error_{self._get_timestamp()}.json"
        return await self.upload_json_data(
            error_data, company_name, "errors", file_name
        )
    
    async def create_company_folders(self, company_name: str) -> None:
        """
        Create folder structure for company in S3.
        
        Args:
            company_name: Company name
        """
        folder_types = [
            "text", "images", "contact", "products", 
            "social_media", "metadata", "raw_html", "sitemap", "errors"
        ]
        
        for folder_type in folder_types:
            folder_key = f"{company_name}/{folder_type}/"
            try:
                # Create empty object to represent folder
                await retry_async(
                    self._upload_file,
                    b"",
                    folder_key,
                    'application/x-directory'
                )
                logger.debug(f"Created folder: {folder_key}")
            except Exception as e:
                logger.warning(f"Could not create folder {folder_key}: {e}")
    
    async def list_company_files(
        self,
        company_name: str,
        data_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files for a company in S3.
        
        Args:
            company_name: Company name
            data_type: Optional data type filter
            
        Returns:
            List of file information
        """
        try:
            prefix = f"{company_name}/"
            if data_type:
                prefix += f"{data_type}/"
            
            response = await retry_async(
                self._list_objects,
                prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': f"s3://{self.bucket_name}/{obj['Key']}"
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files for {company_name}: {e}")
            return []
    
    async def download_file(self, s3_key: str) -> Dict[str, Any]:
        """
        Download and parse JSON file from S3.
        
        Args:
            s3_key: S3 key of the file
            
        Returns:
            Parsed JSON data
        """
        try:
            response = await retry_async(
                self._download_file,
                s3_key
            )
            
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
            
        except Exception as e:
            error_msg = f"Failed to download file {s3_key}: {e}"
            logger.error(error_msg)
            raise S3Error(error_msg, self.bucket_name, s3_key)
    
    async def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3.
        
        Args:
            s3_key: S3 key of the file
            
        Returns:
            True if successful
        """
        try:
            await retry_async(
                self._delete_file,
                s3_key
            )
            logger.info(f"Successfully deleted file: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {s3_key}: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming."""
        from datetime import datetime
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    async def _upload_file(
        self,
        data: bytes,
        s3_key: str,
        content_type: str
    ) -> None:
        """Upload file to S3 (synchronous wrapper for async)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._sync_upload_file,
            data,
            s3_key,
            content_type
        )
    
    def _sync_upload_file(
        self,
        data: bytes,
        s3_key: str,
        content_type: str
    ) -> None:
        """Synchronous upload file to S3."""
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=data,
            ContentType=content_type
        )
    
    async def _list_objects(self, prefix: str) -> Dict[str, Any]:
        """List objects in S3 (synchronous wrapper for async)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_list_objects,
            prefix
        )
    
    def _sync_list_objects(self, prefix: str) -> Dict[str, Any]:
        """Synchronous list objects in S3."""
        return self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix
        )
    
    async def _download_file(self, s3_key: str) -> Dict[str, Any]:
        """Download file from S3 (synchronous wrapper for async)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_download_file,
            s3_key
        )
    
    def _sync_download_file(self, s3_key: str) -> Dict[str, Any]:
        """Synchronous download file from S3."""
        return self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=s3_key
        )
    
    async def _delete_file(self, s3_key: str) -> None:
        """Delete file from S3 (synchronous wrapper for async)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._sync_delete_file,
            s3_key
        )
    
    def _sync_delete_file(self, s3_key: str) -> None:
        """Synchronous delete file from S3."""
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=s3_key
        )


# Global S3 service instance
s3_service = S3Service() 