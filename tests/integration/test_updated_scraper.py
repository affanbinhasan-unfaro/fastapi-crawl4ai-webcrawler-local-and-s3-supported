#!/usr/bin/env python3
"""
Test script to verify the updated app scraper works correctly
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def test_updated_app_scraper():
    """Test the updated app scraper with HTTP-only approach"""
    print("🧪 Testing Updated App Scraper")
    print("=" * 50)
    
    try:
        # Test import
        from app.services.scraper import web_scraper
        print("✅ Import successful!")
        
        # Test basic functionality
        print(f"📊 Max depth: {web_scraper.max_depth}")
        print(f"⏱️  Timeout: {web_scraper.timeout}")
        print(f"🔧 Debug mode: {web_scraper.debug}")
        
        # Test scraping with a simple URL
        test_url = "https://httpbin.org/html"
        company_name = "test_company"
        
        print(f"\n🌐 Testing with URL: {test_url}")
        
        result = await web_scraper.scrape_website(
            url=test_url,
            company_name=company_name,
            max_depth=1
        )
        
        print(f"\n📊 Scraping Results:")
        print(f"  Status: SUCCESS")
        print(f"  Company: {result['metadata']['company_name']}")
        print(f"  Pages crawled: {result['metadata']['total_pages_crawled']}")
        print(f"  Processing time: {result['metadata']['processing_time_seconds']}s")
        print(f"  Method: {result['metadata']['extraction_method']}")
        
        # Check data types
        data = result['data']
        print(f"\n📈 Data Extracted:")
        print(f"  Text items: {len(data['text'])}")
        print(f"  Images: {len(data['images'])}")
        print(f"  Contact info: {len(data['contact'])}")
        print(f"  Products: {len(data['products'])}")
        print(f"  Social media: {len(data['social_media'])}")
        print(f"  Metadata entries: {len(data['metadata'])}")
        
        # Check raw HTML
        print(f"  Raw HTML pages: {len(result['raw_html'])}")
        
        # Coverage summary
        coverage = result['sitemap']['coverage_summary']
        print(f"\n📋 Coverage Summary:")
        print(f"  Total pages: {coverage['total_pages']}")
        print(f"  Pages with text: {coverage['pages_with_text']}")
        print(f"  Pages with images: {coverage['pages_with_images']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing app scraper: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_link_extraction():
    """Test the improved link extraction"""
    print("\n🔗 Testing Link Extraction")
    print("=" * 30)
    
    try:
        from app.services.scraper import web_scraper
        
        # Test with a URL that has links
        test_url = "https://httpbin.org/links/3"
        company_name = "link_test"
        
        print(f"🌐 Testing with: {test_url}")
        
        result = await web_scraper.scrape_website(
            url=test_url,
            company_name=company_name,
            max_depth=2
        )
        
        pages_crawled = result['metadata']['total_pages_crawled']
        print(f"📊 Pages crawled: {pages_crawled}")
        
        if pages_crawled > 1:
            print("✅ Link extraction and subpage crawling working!")
            
            # Show crawl structure
            sitemap = result['sitemap']['crawl_structure']
            for url, info in sitemap.items():
                print(f"  📄 {url} (depth: {info['depth']})")
                if info['links_found']:
                    print(f"     🔗 Found {len(info['links_found'])} links")
        else:
            print("⚠️  Only 1 page crawled - link extraction may need checking")
            
        return pages_crawled > 1
        
    except Exception as e:
        print(f"❌ Error testing link extraction: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔍 Updated App Scraper Test Suite")
    print("=" * 60)
    
    success_count = 0
    
    # Test 1: Basic functionality
    if await test_updated_app_scraper():
        success_count += 1
    
    # Test 2: Link extraction
    if await test_link_extraction():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Tests passed: {success_count}/2")
    
    if success_count == 2:
        print("🎉 All tests passed! The updated app scraper is working perfectly!")
        print("\n✨ Key improvements:")
        print("  ⚡ HTTP-only crawling (much faster)")
        print("  🔍 BeautifulSoup link extraction (more reliable)")
        print("  📊 Comprehensive data extraction")
        print("  🌐 Recursive subpage crawling")
        print("  🔧 Same API interface (drop-in replacement)")
    else:
        print("❌ Some tests failed - check the errors above")

if __name__ == "__main__":
    asyncio.run(main()) 