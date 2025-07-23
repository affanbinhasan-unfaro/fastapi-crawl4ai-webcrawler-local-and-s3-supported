#!/usr/bin/env python3
"""
Test script to verify storage feature flag functionality.
"""
import asyncio
import json
from app.services.storage_service import storage_service
from app.core.config import settings


async def test_storage():
    """Test the storage service functionality."""
    print("=== Storage Service Test ===")
    print(f"SAVE_TO_S3 flag: {settings.save_to_s3}")
    print(f"Storage type: {storage_service.get_storage_type()}")
    
    # Get storage info
    storage_info = storage_service.get_storage_info()
    print(f"Storage info: {json.dumps(storage_info, indent=2)}")
    
    # Test data
    test_data = {
        "test": "data",
        "timestamp": "2024-12-01T12:00:00Z"
    }
    
    company_name = "test_company"
    data_type = "test"
    file_name = "test_file.json"
    
    try:
        # Create folders
        print(f"\nCreating folders for {company_name}...")
        await storage_service.create_company_folders(company_name)
        
        # Upload test data
        print(f"Uploading test data...")
        file_url = await storage_service.upload_json_data(
            test_data, company_name, data_type, file_name
        )
        print(f"Uploaded to: {file_url}")
        
        # List files
        print(f"Listing files for {company_name}...")
        files = await storage_service.list_company_files(company_name)
        print(f"Found {len(files)} files")
        
        # Download and verify
        print(f"Downloading file...")
        downloaded_data = await storage_service.download_file(file_url)
        print(f"Downloaded data: {json.dumps(downloaded_data, indent=2)}")
        
        # Verify data matches
        if downloaded_data == test_data:
            print("✅ Data verification successful!")
        else:
            print("❌ Data verification failed!")
        
        # Clean up
        print(f"Cleaning up...")
        success = await storage_service.delete_file(file_url)
        if success:
            print("✅ File deleted successfully!")
        else:
            print("❌ File deletion failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")


if __name__ == "__main__":
    asyncio.run(test_storage()) 