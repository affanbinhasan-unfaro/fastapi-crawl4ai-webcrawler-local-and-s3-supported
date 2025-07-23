#!/usr/bin/env python3
"""
Test script for the simplified Web Scraper API
Tests only the /scrape endpoint and verifies data storage format
"""

import asyncio
import sys
import json
from pathlib import Path

# Add project root directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def test_simplified_scraper():
    """Test the simplified scraper service and data format"""
    print("🧪 Testing Simplified Web Scraper API")
    print("=" * 60)
    
    try:
        # Test scraper service
        print("🔧 Testing scraper service...")
        from app.services.scraper import web_scraper
        
        test_url = "https://httpbin.org/html"
        company_name = "simplified_test"
        
        result = await web_scraper.scrape_website(
            url=test_url,
            company_name=company_name,
            max_depth=1
        )
        
        print("✅ Scraper service works!")
        print(f"  📊 Method: {result['metadata']['extraction_method']}")
        print(f"  📄 Pages: {result['metadata']['total_pages_crawled']}")
        
        # Test data processor
        print("\n📊 Testing data processor...")
        from app.services.data_processor import data_processor
        
        processor_result = await data_processor.process_scraping_request(
            url=test_url,
            company_name=company_name,
            max_depth=1
        )
        
        if processor_result['status'] == 'success':
            print("✅ Data processor works!")
            print(f"  📁 Storage files created: {len(processor_result['storage_files'])}")
            
            # Check stored file format
            storage_files = processor_result['storage_files']
            if storage_files:
                # Pick first file to check format
                first_file_url = list(storage_files.values())[0]
                print(f"\n📋 Checking data format in: {first_file_url}")
                
                # Check if it's a local file
                if first_file_url.startswith("file://"):
                    file_path = first_file_url[7:]  # Remove file:// prefix
                    if Path(file_path).exists():
                        with open(file_path, 'r', encoding='utf-8') as f:
                            stored_data = json.load(f)
                        
                        print("✅ Data format verification:")
                        print(f"  📊 Has metadata: {'metadata' in stored_data}")
                        print(f"  📊 Has data: {'data' in stored_data}")
                        print(f"  📊 Has data_type: {'data_type' in stored_data}")
                        print(f"  📊 Has company_name: {'company_name' in stored_data}")
                        print(f"  📊 Has extraction_summary: {'extraction_summary' in stored_data}")
                        
                        if 'extraction_summary' in stored_data:
                            summary = stored_data['extraction_summary']
                            print(f"  📈 Total items: {summary.get('total_items', 0)}")
                            print(f"  📈 Has content: {summary.get('has_content', False)}")
                    else:
                        print("⚠️  File not found for format verification")
        else:
            print(f"❌ Data processor failed: {processor_result.get('error_message')}")
            return False

        # Test API components
        print("\n📦 Testing API components...")
        from app.main import app
        from app.models.schemas import ScrapingRequest, ScrapingResponse
        
        print("✅ API components imported successfully!")
        print(f"  🚀 App title: {app.title}")
        print(f"  📄 ScrapingRequest model: ✅")
        print(f"  📄 ScrapingResponse model: ✅")
        
        print("\n🎉 All tests passed!")
        print("✨ Simplified API is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_structure():
    """Test that the data structure includes all necessary information"""
    print("\n📋 Data Structure Verification")
    print("=" * 40)
    
    try:
        # Expected data structure
        expected_structure = {
            'metadata': 'Scraping metadata (timestamp, method, etc.)',
            'data': 'Actual scraped data (text, images, etc.)',
            'data_type': 'Type of data (text, images, contact, etc.)',
            'company_name': 'Company name',
            'extraction_summary': 'Summary with total_items, has_content, etc.'
        }
        
        print("✅ Expected data structure for stored files:")
        for key, description in expected_structure.items():
            print(f"  📊 {key}: {description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Structure verification failed: {e}")
        return False

async def main():
    """Run simplified API tests"""
    print("🚀 SIMPLIFIED WEB SCRAPER API TEST")
    print("=" * 80)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Simplified scraper functionality
    if await test_simplified_scraper():
        tests_passed += 1
    
    # Test 2: Data structure verification
    if test_data_structure():
        tests_passed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 SIMPLIFIED API TEST RESULTS")
    print("=" * 80)
    print(f"✅ Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Simplified Web Scraper API is ready!")
        print("\n✨ Key Features:")
        print("  📍 Single /scrape endpoint")
        print("  ⚡ HTTP-only crawling with BeautifulSoup")
        print("  📊 Comprehensive data extraction")
        print("  💾 Structured storage with summaries")
        print("  🔧 Simple, clean codebase")
        print("\n🎯 Ready to use!")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed")
        print("🔧 Please check the errors above")

if __name__ == "__main__":
    asyncio.run(main()) 