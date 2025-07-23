#!/usr/bin/env python3
"""
Debug script to test link extraction and understand why subpages aren't being crawled
"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def debug_link_extraction():
    """Test link extraction to see what's happening"""
    print("🔍 Debugging Link Extraction")
    print("=" * 50)
    
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        
        # Test with a website that definitely has links
        test_url = "https://example.com"
        
        print(f"🌐 Testing URL: {test_url}")
        
        # Create extraction schema focused on links
        extraction_schema = {
            "name": "LinkDebugger",
            "baseSelector": "body",
            "fields": [
                {"name": "all_links", "selector": "a", "type": "text", "multiple": True},
                {"name": "all_hrefs", "selector": "a[href]", "type": "attribute", "attribute": "href", "multiple": True},
                {"name": "link_count", "selector": "a", "type": "text", "multiple": True},
                {"name": "page_title", "selector": "title", "type": "text"},
                {"name": "all_text", "selector": "body", "type": "text"}
            ]
        }
        
        config = CrawlerRunConfig(
            verbose=True,
            word_count_threshold=1,
            cache_mode="bypass",
            extraction_strategy=JsonCssExtractionStrategy(extraction_schema)
        )
        
        # Create HTTP strategy
        http_strategy = AsyncHTTPCrawlerStrategy()
        
        async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
            result = await crawler.arun(url=test_url, config=config)
            
            print(f"\n📊 Crawl Results:")
            print(f"  Success: {result.success}")
            print(f"  Status Code: {getattr(result, 'status_code', 'N/A')}")
            print(f"  HTML Length: {len(result.html) if hasattr(result, 'html') and result.html else 0}")
            
            # Debug the raw HTML
            if hasattr(result, 'html') and result.html:
                print(f"\n🔍 Raw HTML Analysis:")
                html_content = result.html
                link_count = html_content.count('<a ')
                href_count = html_content.count('href=')
                print(f"  <a> tags found in HTML: {link_count}")
                print(f"  href attributes found: {href_count}")
                
                # Show first few links
                import re
                links = re.findall(r'<a[^>]*href=[\'"]([^\'"]*)[\'"][^>]*>(.*?)</a>', html_content, re.IGNORECASE | re.DOTALL)
                print(f"  Links found by regex: {len(links)}")
                for i, (href, text) in enumerate(links[:3]):
                    print(f"    {i+1}. {href} -> {text.strip()[:50]}...")
            
            # Debug extracted content
            if hasattr(result, 'extracted_content') and result.extracted_content:
                try:
                    if isinstance(result.extracted_content, str):
                        extracted = json.loads(result.extracted_content)
                    else:
                        extracted = result.extracted_content
                    
                    print(f"\n🔍 Extracted Content Analysis:")
                    print(f"  Type: {type(extracted)}")
                    
                    if isinstance(extracted, list) and len(extracted) > 0:
                        extracted = extracted[0]  # Take first item if list
                    
                    if isinstance(extracted, dict):
                        print(f"  Keys found: {list(extracted.keys())}")
                        
                        all_hrefs = extracted.get('all_hrefs', [])
                        all_links = extracted.get('all_links', [])
                        
                        print(f"  HREFs extracted: {len(all_hrefs)}")
                        print(f"  Link texts extracted: {len(all_links)}")
                        
                        if all_hrefs:
                            print(f"  Sample HREFs:")
                            for i, href in enumerate(all_hrefs[:5]):
                                text = all_links[i] if i < len(all_links) else "No text"
                                print(f"    {i+1}. {href} -> {text}")
                        
                        print(f"  Page Title: {extracted.get('page_title', 'No title')}")
                    
                    print(f"\n📄 Full extracted content:")
                    print(json.dumps(extracted, indent=2)[:500] + "...")
                    
                except Exception as e:
                    print(f"  ❌ Error parsing extracted content: {e}")
                    print(f"  Raw content: {str(result.extracted_content)[:200]}...")
            
            return result.success
            
    except Exception as e:
        print(f"❌ Error in link extraction debug: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_different_websites():
    """Test link extraction on different types of websites"""
    print("\n🌐 Testing Different Websites")
    print("=" * 50)
    
    test_urls = [
        "https://httpbin.org/links/5",  # This should have 5 links
        "https://www.iana.org/domains/example",  # This should have navigation links
    ]
    
    for url in test_urls:
        print(f"\n🔗 Testing: {url}")
        
        try:
            from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
            from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
            from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
            
            extraction_schema = {
                "name": "LinkTester",
                "baseSelector": "body",
                "fields": [
                    {"name": "links", "selector": "a[href]", "type": "attribute", "attribute": "href", "multiple": True},
                    {"name": "link_texts", "selector": "a[href]", "type": "text", "multiple": True}
                ]
            }
            
            config = CrawlerRunConfig(
                verbose=False,
                word_count_threshold=1,
                cache_mode="bypass",
                extraction_strategy=JsonCssExtractionStrategy(extraction_schema)
            )
            
            http_strategy = AsyncHTTPCrawlerStrategy()
            
            async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
                result = await crawler.arun(url=url, config=config)
                
                if result.success and hasattr(result, 'extracted_content'):
                    try:
                        extracted = json.loads(result.extracted_content) if isinstance(result.extracted_content, str) else result.extracted_content
                        if isinstance(extracted, list) and len(extracted) > 0:
                            extracted = extracted[0]
                        
                        if isinstance(extracted, dict):
                            links = extracted.get('links', [])
                            link_texts = extracted.get('link_texts', [])
                            print(f"  ✅ Found {len(links)} links")
                            for i, link in enumerate(links[:3]):
                                text = link_texts[i] if i < len(link_texts) else "No text"
                                print(f"    {i+1}. {link} -> {text}")
                        else:
                            print(f"  ❌ Extracted content is not a dict: {type(extracted)}")
                    except Exception as e:
                        print(f"  ❌ Error processing: {e}")
                else:
                    print(f"  ❌ Failed to crawl")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")

async def main():
    """Run all debug tests"""
    print("🔍 Link Extraction Debug Tool")
    print("=" * 60)
    
    # Test 1: Basic link extraction
    await debug_link_extraction()
    
    # Test 2: Different websites
    await test_different_websites()
    
    print("\n" + "=" * 60)
    print("🎯 Debug complete! Check the results above to understand why links aren't being found.")

if __name__ == "__main__":
    asyncio.run(main()) 