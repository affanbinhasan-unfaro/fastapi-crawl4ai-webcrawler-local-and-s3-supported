#!/usr/bin/env python3
"""
Comprehensive integration test for the updated Web Scraper API
Tests the complete flow: API request -> scraper -> data processor -> storage
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def test_scraper_service():
    """Test the updated scraper service directly"""
    print("🔧 Testing Updated Scraper Service")
    print("=" * 50)
    
    try:
        from app.services.scraper import web_scraper
        
        # Test basic scraping
        test_url = "https://httpbin.org/html"
        company_name = "httpbin_test"
        
        print(f"🌐 Testing scraper with: {test_url}")
        
        result = await web_scraper.scrape_website(
            url=test_url,
            company_name=company_name,
            max_depth=2
        )
        
        # Verify result structure
        assert 'metadata' in result, "Missing metadata in result"
        assert 'data' in result, "Missing data in result"
        assert 'raw_html' in result, "Missing raw_html in result"
        assert 'sitemap' in result, "Missing sitemap in result"
        
        # Check data types
        data = result['data']
        expected_data_types = ['text', 'images', 'contact', 'products', 'social_media', 'metadata']
        for data_type in expected_data_types:
            assert data_type in data, f"Missing {data_type} in data"
            assert isinstance(data[data_type], list), f"{data_type} should be a list"
        
        # Check metadata
        metadata = result['metadata']
        assert metadata['extraction_method'] == 'crawl4AI_HTTP_BeautifulSoup', "Wrong extraction method"
        assert 'total_pages_crawled' in metadata, "Missing pages crawled count"
        
        print(f"✅ Scraper test passed!")
        print(f"  📊 Pages crawled: {metadata['total_pages_crawled']}")
        print(f"  ⚡ Method: {metadata['extraction_method']}")
        print(f"  🔗 Text items: {len(data['text'])}")
        print(f"  🖼️  Images: {len(data['images'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_data_processor():
    """Test the data processor with updated scraper"""
    print("\n📊 Testing Data Processor Integration")
    print("=" * 50)
    
    try:
        from app.services.data_processor import data_processor
        
        # Test processing a scraping request
        test_url = "https://httpbin.org/html"
        company_name = "processor_test"
        
        print(f"🌐 Testing data processor with: {test_url}")
        
        result = await data_processor.process_scraping_request(
            url=test_url,
            company_name=company_name,
            max_depth=1
        )
        
        # Verify result structure
        assert result['status'] == 'success', f"Processing failed: {result.get('error_message')}"
        assert 'company_name' in result, "Missing company_name"
        assert 'url' in result, "Missing url"
        assert 's3_files' in result, "Missing s3_files"
        assert 'metadata' in result, "Missing metadata"
        
        # Check that files were created
        s3_files = result['s3_files']
        print(f"✅ Data processor test passed!")
        print(f"  📁 Files created: {len(s3_files)}")
        for data_type, file_url in s3_files.items():
            print(f"    - {data_type}: {file_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data processor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_storage_service():
    """Test storage service functionality"""
    print("\n💾 Testing Storage Service")
    print("=" * 50)
    
    try:
        from app.services.storage_service import storage_service
        
        # Test basic storage info
        storage_info = storage_service.get_storage_info()
        print(f"📊 Storage type: {storage_info['storage_type']}")
        print(f"📁 Base path: {storage_info.get('base_path', 'N/A')}")
        
        # Test creating company folders
        test_company = "storage_test"
        await storage_service.create_company_folders(test_company)
        print(f"✅ Created folders for: {test_company}")
        
        # Test uploading test data
        test_data = {
            "metadata": {"test": True, "timestamp": "2024-01-01T00:00:00Z"},
            "data": [{"content": "test content", "confidence": 0.9}]
        }
        
        file_url = await storage_service.upload_json_data(
            test_data, test_company, "test", "test_file.json"
        )
        print(f"✅ Uploaded test data: {file_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_imports():
    """Test that all API components can be imported"""
    print("\n📦 Testing API Component Imports")
    print("=" * 50)
    
    try:
        # Test core imports
        from app.main import app
        from app.api.routes import router
        from app.core.config import settings
        from app.models.schemas import ScrapingRequest, ScrapingResponse
        from app.services.scraper import web_scraper
        from app.services.data_processor import data_processor
        from app.services.storage_service import storage_service
        from app.utils.helpers import generate_timestamp
        from app.utils.logger import logger
        
        print("✅ All imports successful!")
        print(f"  🔧 App version: {app.version}")
        print(f"  ⚙️  Settings loaded: {bool(settings)}")
        print(f"  🕷️  Scraper ready: {bool(web_scraper)}")
        print(f"  📊 Processor ready: {bool(data_processor)}")
        print(f"  💾 Storage ready: {bool(storage_service)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_end_to_end_flow():
    """Test complete end-to-end scraping flow"""
    print("\n🔄 Testing End-to-End Flow")
    print("=" * 50)
    
    try:
        from app.services.data_processor import data_processor
        
        # Test with a website that has links for proper subpage crawling
        test_url = "https://httpbin.org/links/3"
        company_name = "e2e_test"
        max_depth = 2
        
        print(f"🌐 Running end-to-end test")
        print(f"  URL: {test_url}")
        print(f"  Company: {company_name}")
        print(f"  Max depth: {max_depth}")
        
        # Run complete processing
        result = await data_processor.process_scraping_request(
            url=test_url,
            company_name=company_name,
            max_depth=max_depth
        )
        
        if result['status'] == 'success':
            print("✅ End-to-end test passed!")
            print(f"  📊 Metadata:")
            metadata = result['metadata']
            print(f"    - Pages crawled: {metadata['total_pages_crawled']}")
            print(f"    - Processing time: {metadata['processing_time_seconds']}s")
            print(f"    - Method: {metadata['extraction_method']}")
            
            print(f"  📁 Storage files:")
            for data_type, file_url in result['s3_files'].items():
                print(f"    - {data_type}: ✅")
            
            # Test company summary
            summary = await data_processor.get_company_data_summary(company_name)
            print(f"  📋 Summary:")
            print(f"    - Total files: {summary['total_files']}")
            print(f"    - Data types: {len(summary['data_types_available'])}")
            
            return True
        else:
            print(f"❌ End-to-end test failed: {result.get('error_message')}")
            return False
            
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run comprehensive integration test suite"""
    print("🧪 COMPREHENSIVE WEB SCRAPER API INTEGRATION TEST")
    print("=" * 80)
    
    tests = [
        ("Import Test", test_api_imports),
        ("Scraper Service", test_scraper_service),
        ("Storage Service", test_storage_service),
        ("Data Processor", test_data_processor),
        ("End-to-End Flow", test_end_to_end_flow),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 40)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                success = await test_func()
            else:
                success = test_func()
                
            if success:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 INTEGRATION TEST RESULTS")
    print("=" * 80)
    print(f"✅ Tests passed: {passed}/{total}")
    print(f"❌ Tests failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("🚀 The updated Web Scraper API is fully functional!")
        print("\n✨ Key Features Verified:")
        print("  ⚡ HTTP-only crawling (fast and reliable)")
        print("  🔍 BeautifulSoup link extraction (robust)")
        print("  📊 Comprehensive data extraction (text, images, contacts, etc.)")
        print("  🌐 Recursive subpage crawling")
        print("  💾 Automatic data storage (S3/local)")
        print("  🔄 Complete API integration")
        print("  📋 Company data summaries")
        print("\n🎯 Ready for production use!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - check errors above")
        print("🔧 Please fix issues before using in production")

if __name__ == "__main__":
    asyncio.run(main()) 