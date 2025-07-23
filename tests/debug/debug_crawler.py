#!/usr/bin/env python3
"""
Debug script to test HTTP crawling and identify issues
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def test_basic_http_crawl():
    """Test basic HTTP crawling with minimal configuration"""
    print("🧪 Testing basic HTTP crawling...")
    
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
        
        # Simple test URL
        test_url = "https://httpbin.org/html"
        
        print(f"🌐 Testing URL: {test_url}")
        
        # Create HTTP strategy
        http_strategy = AsyncHTTPCrawlerStrategy()
        
        # Simple configuration
        config = CrawlerRunConfig(
            verbose=True,
            word_count_threshold=1,  # Very low threshold
            cache_mode="bypass"
        )
        
        async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
            print("✅ Crawler created successfully")
            
            result = await crawler.arun(url=test_url, config=config)
            
            print(f"📊 Crawl result:")
            print(f"  Success: {result.success}")
            print(f"  Status Code: {getattr(result, 'status_code', 'N/A')}")
            print(f"  HTML Length: {len(result.html) if hasattr(result, 'html') and result.html else 0}")
            print(f"  Cleaned HTML Length: {len(result.cleaned_html) if hasattr(result, 'cleaned_html') and result.cleaned_html else 0}")
            print(f"  Markdown Length: {len(result.markdown) if hasattr(result, 'markdown') and result.markdown else 0}")
            print(f"  Error: {getattr(result, 'error_message', 'None')}")
            
            if hasattr(result, 'links') and result.links:
                print(f"  Links found: {len(result.links)}")
            
            if not result.success:
                print(f"❌ Crawl failed: {result.error_message}")
                return False
            else:
                print("✅ Basic HTTP crawl successful!")
                return True
                
    except Exception as e:
        print(f"❌ Error in basic HTTP crawl test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_browser_crawl_fallback():
    """Test browser-based crawling as fallback"""
    print("\n🧪 Testing browser-based crawling as fallback...")
    
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        
        # Simple test URL
        test_url = "https://httpbin.org/html"
        
        print(f"🌐 Testing URL: {test_url}")
        
        # Browser configuration
        browser_config = BrowserConfig(
            headless=True,
            verbose=True
        )
        
        # Simple configuration
        config = CrawlerRunConfig(
            verbose=True,
            word_count_threshold=1,
            cache_mode="bypass",
            page_timeout=10000  # 10 seconds
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print("✅ Browser crawler created successfully")
            
            result = await crawler.arun(url=test_url, config=config)
            
            print(f"📊 Browser crawl result:")
            print(f"  Success: {result.success}")
            print(f"  Status Code: {getattr(result, 'status_code', 'N/A')}")
            print(f"  HTML Length: {len(result.html) if hasattr(result, 'html') and result.html else 0}")
            print(f"  Cleaned HTML Length: {len(result.cleaned_html) if hasattr(result, 'cleaned_html') and result.cleaned_html else 0}")
            print(f"  Markdown Length: {len(result.markdown) if hasattr(result, 'markdown') and result.markdown else 0}")
            print(f"  Error: {getattr(result, 'error_message', 'None')}")
            
            if not result.success:
                print(f"❌ Browser crawl failed: {result.error_message}")
                return False
            else:
                print("✅ Browser crawl successful!")
                return True
                
    except Exception as e:
        print(f"❌ Error in browser crawl test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_extraction_strategy():
    """Test extraction strategy with a working crawler"""
    print("\n🧪 Testing extraction strategy...")
    
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        
        # Simple test URL
        test_url = "https://httpbin.org/html"
        
        # Create extraction schema
        extraction_schema = {
            "name": "TestExtractor",
            "baseSelector": "body",
            "fields": [
                {"name": "title", "selector": "title", "type": "text"},
                {"name": "headings", "selector": "h1", "type": "text", "multiple": True},
                {"name": "links", "selector": "a[href]", "type": "attribute", "attribute": "href", "multiple": True}
            ]
        }
        
        # Browser configuration
        browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )
        
        # Configuration with extraction
        config = CrawlerRunConfig(
            verbose=True,
            word_count_threshold=1,
            cache_mode="bypass",
            extraction_strategy=JsonCssExtractionStrategy(extraction_schema)
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=test_url, config=config)
            
            print(f"📊 Extraction test result:")
            print(f"  Success: {result.success}")
            print(f"  Has extracted content: {hasattr(result, 'extracted_content') and result.extracted_content is not None}")
            
            if hasattr(result, 'extracted_content') and result.extracted_content:
                print(f"  Extracted content length: {len(str(result.extracted_content))}")
                print(f"  Extracted content preview: {str(result.extracted_content)[:200]}...")
                
            return result.success
                
    except Exception as e:
        print(f"❌ Error in extraction strategy test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run diagnostic tests"""
    print("🔍 Crawl4ai HTTP Strategy Diagnostic Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic HTTP crawl
    if await test_basic_http_crawl():
        tests_passed += 1
    
    # Test 2: Browser crawl fallback
    if await test_browser_crawl_fallback():
        tests_passed += 1
    
    # Test 3: Extraction strategy
    if await test_extraction_strategy():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Diagnostic results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed > 0:
        print("✅ At least one crawling method works!")
        if tests_passed < total_tests:
            print("⚠️  Some methods failed - we'll use the working ones")
    else:
        print("❌ All crawling methods failed")
        print("🔧 Possible issues:")
        print("  - Network connectivity problems")
        print("  - crawl4ai installation issues")
        print("  - Missing dependencies")
        
    return tests_passed > 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 