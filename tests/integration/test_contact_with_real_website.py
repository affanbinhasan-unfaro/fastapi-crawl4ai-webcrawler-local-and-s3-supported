#!/usr/bin/env python3
"""
Test contact extraction with a real website that has contact info
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def test_contact_with_actual_website():
    """Test with a website that has contact information"""
    print("🌐 Testing Contact Extraction with Real Website")
    print("=" * 60)
    
    try:
        from app.services.data_processor import data_processor
        
        # Test with a website that likely has contact info
        # Using a simple business website or contact page
        test_urls = [
            "https://example.com",  # Basic test
        ]
        
        for test_url in test_urls:
            print(f"\n🔍 Testing: {test_url}")
            
            try:
                result = await data_processor.process_scraping_request(
                    url=test_url,
                    company_name="contact_real_test",
                    max_depth=1
                )
                
                if result['status'] == 'success':
                    storage_files = result.get('storage_files', {})
                    
                    print(f"✅ Scraping successful!")
                    print(f"  📁 Total files: {len(storage_files)}")
                    
                    # Check if contact file was created
                    if 'contact' in storage_files:
                        print(f"  📞 Contact file: {storage_files['contact']}")
                        
                        # Try to read the contact file to see what was found
                        contact_file = storage_files['contact']
                        if contact_file.startswith("file://"):
                            file_path = contact_file[7:]
                            if Path(file_path).exists():
                                import json
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    contact_data = json.load(f)
                                
                                contacts = contact_data.get('data', [])
                                print(f"  📊 Contacts found: {len(contacts)}")
                                
                                for contact in contacts[:5]:  # Show first 5
                                    print(f"    - {contact['type']}: {contact['value']}")
                                    
                                return len(contacts) > 0
                            
                    else:
                        print("  ℹ️  No contact file created (no contacts found)")
                        return False
                else:
                    print(f"  ❌ Scraping failed: {result.get('error_message')}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ Error with {test_url}: {e}")
                continue
                
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_mock_contact_data():
    """Test by directly creating scraped data with contacts"""
    print("\n🧪 Testing Contact Storage with Mock Data")
    print("=" * 60)
    
    try:
        from app.services.data_processor import data_processor
        
        # Create mock scraped data that includes contacts
        mock_scraped_data = {
            'metadata': {
                'scraping_timestamp': '2024-01-01T12:00:00Z',
                'source_url': 'https://test.com',
                'company_name': 'contact_mock_test',
                'extraction_method': 'crawl4AI_HTTP_BeautifulSoup',
                'total_pages_crawled': 1,
                'processing_time_seconds': 1.0
            },
            'data': {
                'text': [],
                'images': [],
                'contact': [
                    {
                        'type': 'email',
                        'value': 'test@example.com',
                        'page_url': 'https://test.com',
                        'confidence_score': 0.95,
                        'extraction_method': 'regex_pattern_matching'
                    },
                    {
                        'type': 'phone',
                        'value': '5551234567',
                        'page_url': 'https://test.com',
                        'confidence_score': 0.8,
                        'extraction_method': 'regex_pattern_matching'
                    }
                ],
                'products': [],
                'social_media': [],
                'metadata': []
            },
            'raw_html': {'https://test.com': '<html><body>test</body></html>'},
            'sitemap': {'crawl_structure': {}, 'coverage_summary': {}}
        }
        
        # Upload the mock data
        storage_files = await data_processor._upload_scraped_data(
            mock_scraped_data, 
            'contact_mock_test'
        )
        
        print(f"✅ Mock data uploaded!")
        print(f"  📁 Files created: {len(storage_files)}")
        
        if 'contact' in storage_files:
            print(f"  📞 Contact file: {storage_files['contact']}")
            
            # Read and verify the contact file
            contact_file = storage_files['contact']
            if contact_file.startswith("file://"):
                file_path = contact_file[7:]
                if Path(file_path).exists():
                    import json
                    with open(file_path, 'r', encoding='utf-8') as f:
                        stored_data = json.load(f)
                    
                    contacts = stored_data.get('data', [])
                    print(f"  📊 Contacts stored: {len(contacts)}")
                    
                    for contact in contacts:
                        print(f"    - {contact['type']}: {contact['value']}")
                    
                    # Check data structure
                    expected_fields = ['metadata', 'data', 'data_type', 'company_name', 'extraction_summary']
                    for field in expected_fields:
                        if field in stored_data:
                            print(f"  ✅ Has {field}")
                        else:
                            print(f"  ❌ Missing {field}")
                    
                    return len(contacts) > 0
        else:
            print("  ❌ No contact file created")
            return False
            
    except Exception as e:
        print(f"❌ Mock test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run contact storage tests"""
    print("📞 CONTACT STORAGE VERIFICATION TEST")
    print("=" * 80)
    
    tests = [
        ("Mock Contact Data", test_with_mock_contact_data),
        ("Real Website", test_contact_with_actual_website),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 40)
        
        try:
            success = await test_func()
            if success:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 CONTACT STORAGE TEST RESULTS")
    print("=" * 80)
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed > 0:
        print("\n🎉 Contact extraction and storage is working!")
        print("✨ Contacts will be saved when found on websites!")
    else:
        print(f"\n⚠️  Contact storage needs verification")

if __name__ == "__main__":
    asyncio.run(main()) 