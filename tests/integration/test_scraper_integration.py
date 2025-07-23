#!/usr/bin/env python3
"""
Quick integration test for updated scraper service
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def test_scraper_integration():
    """Test scraper integration with the app services"""
    print("🧪 Testing Scraper Integration")
    print("=" * 50)
    
    try:
        # Test import
        print("📦 Testing imports...")
        from app.services.scraper import web_scraper
        from app.services.data_processor import data_processor
        print("✅ Imports successful!")
        
        # Test scraper directly
        print("\n🕷️ Testing scraper service...")
        test_url = "https://httpbin.org/html"
        company_name = "integration_test"
        
        result = await web_scraper.scrape_website(
            url=test_url,
            company_name=company_name,
            max_depth=1
        )
        
        print(f"✅ Scraper worked!")
        print(f"  📊 Method: {result['metadata']['extraction_method']}")
        print(f"  📄 Pages: {result['metadata']['total_pages_crawled']}")
        print(f"  🔍 Text items: {len(result['data']['text'])}")
        
        # Test data processor
        print("\n📊 Testing data processor...")
        processor_result = await data_processor.process_scraping_request(
            url=test_url,
            company_name=company_name + "_processor", 
            max_depth=1
        )
        
        if processor_result['status'] == 'success':
            print("✅ Data processor worked!")
            print(f"  📁 Files created: {len(processor_result['s3_files'])}")
            for data_type in processor_result['s3_files']:
                print(f"    - {data_type}")
        else:
            print(f"❌ Data processor failed: {processor_result.get('error_message')}")
            return False
        
        print("\n🎉 Integration test successful!")
        print("✨ The updated scraper is fully integrated and working!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_scraper_integration()) 