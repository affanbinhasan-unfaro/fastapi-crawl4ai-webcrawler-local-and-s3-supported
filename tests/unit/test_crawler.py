#!/usr/bin/env python3
"""
Simple test script to verify server-side crawler functionality
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def test_imports():
    """Test that all imports work correctly for server-side crawling"""
    try:
        from main import ServerSideWebCrawler
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        print("✅ All server-side crawler imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def test_basic_functionality():
    """Test basic server-side crawler setup"""
    try:
        from main import ServerSideWebCrawler
        
        # Test crawler initialization
        crawler = ServerSideWebCrawler(
            base_url="https://httpbin.org",
            company_name="httpbin_test", 
            max_depth=2,
            max_pages=5
        )
        
        print(f"✅ Server-side crawler initialized successfully!")
        print(f"📁 Output directory: {crawler.output_dir}")
        print(f"🏢 Company name: {crawler.company_name}")
        print(f"🔗 Base URL: {crawler.base_url}")
        print(f"🌐 Crawling method: HTTP requests (no browser)")
        
        return True
    except Exception as e:
        print(f"❌ Crawler initialization error: {e}")
        return False

async def test_http_strategy():
    """Test HTTP crawler strategy setup"""
    try:
        from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
        from crawl4ai import AsyncWebCrawler
        
        # Test HTTP strategy
        http_strategy = AsyncHTTPCrawlerStrategy()
        print("✅ HTTP crawler strategy created successfully!")
        
        # Test crawler with HTTP strategy
        async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
            print("✅ HTTP-based crawler initialized successfully!")
            return True
            
    except Exception as e:
        print(f"❌ HTTP strategy error: {e}")
        return False

async def test_extraction_schema():
    """Test extraction schema configuration"""
    try:
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        
        # Test extraction schema similar to what's used in the crawler
        test_schema = {
            "name": "TestExtractor",
            "baseSelector": "body",
            "fields": [
                {"name": "title", "selector": "title", "type": "text"},
                {"name": "links", "selector": "a[href]", "type": "attribute", "attribute": "href", "multiple": True},
                {"name": "headings", "selector": "h1, h2, h3", "type": "text", "multiple": True}
            ]
        }
        
        extraction_strategy = JsonCssExtractionStrategy(test_schema)
        print("✅ Extraction schema configured successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Extraction schema error: {e}")
        return False

async def main():
    """Run all tests for server-side crawler"""
    print("🧪 Testing Server-Side Web Crawler Setup")
    print("🌐 HTTP-based crawling (no browser required)")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: imports
    print("\n1. Testing imports...")
    if await test_imports():
        tests_passed += 1
    
    # Test 2: basic functionality
    print("\n2. Testing basic functionality...")
    if await test_basic_functionality():
        tests_passed += 1
    
    # Test 3: HTTP strategy
    print("\n3. Testing HTTP crawler strategy...")
    if await test_http_strategy():
        tests_passed += 1
    
    # Test 4: extraction schema
    print("\n4. Testing extraction schema...")
    if await test_extraction_schema():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The server-side crawler is ready to use.")
        print("\n🚀 Key advantages of server-side crawling:")
        print("  ⚡ Much faster than browser-based crawling")
        print("  💾 Lower memory usage")
        print("  🚫 No browser dependencies required")
        print("  🌐 Pure HTTP requests with HTML parsing")
        print("\n🔧 To run the crawler:")
        print("  python main.py https://example.com")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
    return tests_passed == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 