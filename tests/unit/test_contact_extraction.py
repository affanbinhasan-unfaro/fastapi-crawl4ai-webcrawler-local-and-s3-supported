#!/usr/bin/env python3
"""
Test script to verify contact extraction logic
"""

import asyncio
import sys
from pathlib import Path

# Add project root directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_contact_extraction_with_sample_html():
    """Test contact extraction with sample HTML containing contacts"""
    print("🔍 Testing Contact Extraction Logic")
    print("=" * 60)
    
    try:
        from app.services.scraper import web_scraper
        from bs4 import BeautifulSoup
        
        # Sample HTML with various contact formats
        sample_html = """
        <html>
        <body>
            <h1>Contact Us</h1>
            <div class="contact-info">
                <p>Email us at: contact@example.com or info@test.org</p>
                <p>Call us: (555) 123-4567</p>
                <p>Phone: +1-800-555-0123</p>
                <p>International: +44 20 1234 5678</p>
                <div class="footer">
                    <p>Support: support@company.com</p>
                    <p>Sales: 555.987.6543</p>
                    <p>Fax: 555 444 3333</p>
                </div>
                <p>Alternative contact: john.doe@business.net</p>
                <p>Emergency: 911</p>
                <p>Office: (212) 555-1234 ext. 567</p>
            </div>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        # Test contact extraction
        contacts = web_scraper._extract_contact_comprehensive(soup, "https://example.com")
        
        print(f"📊 Contacts extracted: {len(contacts)}")
        
        # Group by type
        emails = [c for c in contacts if c['type'] == 'email']
        phones = [c for c in contacts if c['type'] == 'phone']
        
        print(f"📧 Emails found: {len(emails)}")
        for email in emails:
            print(f"   - {email['value']} (confidence: {email['confidence_score']})")
        
        print(f"📞 Phones found: {len(phones)}")
        for phone in phones:
            print(f"   - {phone['value']} (confidence: {phone['confidence_score']})")
        
        if len(contacts) > 0:
            print("✅ Contact extraction is working!")
            return True
        else:
            print("❌ No contacts extracted - there might be an issue with the patterns")
            return False
            
    except Exception as e:
        print(f"❌ Contact extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_contact_with_real_website():
    """Test contact extraction with a real website"""
    print("\n🌐 Testing Contact Extraction with Real Website")
    print("=" * 60)
    
    try:
        from app.services.scraper import web_scraper
        
        # Test with a website that likely has contact info
        test_url = "https://httpbin.org/html"  # This won't have contacts
        print(f"🔍 Testing with: {test_url}")
        print("ℹ️  Note: This test site may not have contact info")
        
        result = await web_scraper.scrape_website(
            url=test_url,
            company_name="contact_test",
            max_depth=1
        )
        
        contacts = result['data']['contact']
        print(f"📊 Contacts found: {len(contacts)}")
        
        if len(contacts) > 0:
            for contact in contacts:
                print(f"   - {contact['type']}: {contact['value']}")
        else:
            print("ℹ️  No contacts found (expected for this test site)")
        
        return True
        
    except Exception as e:
        print(f"❌ Real website test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_improved_contact_patterns():
    """Test with improved contact extraction patterns"""
    print("\n🔧 Testing Improved Contact Patterns")
    print("=" * 60)
    
    try:
        import re
        
        # Test text with various contact formats
        test_text = """
        Contact us at hello@company.com or support@test.co.uk
        Call: (555) 123-4567, +1 800 555 0123, 555.987.6543
        International: +44 20 1234 5678, +91-9876543210
        Fax: 555 444 3333
        """
        
        # Current email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, test_text)
        print(f"📧 Emails found: {emails}")
        
        # Current phone patterns
        phone_patterns = [
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            r'\b\+?[1-9]\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b'
        ]
        
        all_phones = []
        for pattern in phone_patterns:
            phones = re.findall(pattern, test_text)
            all_phones.extend(phones)
        
        print(f"📞 Phones found: {all_phones}")
        
        # Improved phone pattern
        improved_phone_pattern = r'(?:\+?[\d\s\-\(\)\.]{10,})'
        improved_phones = re.findall(improved_phone_pattern, test_text)
        print(f"🔧 Improved phones: {improved_phones}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern test failed: {e}")
        return False

async def main():
    """Run contact extraction tests"""
    print("📞 CONTACT EXTRACTION TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("HTML Sample Test", test_contact_extraction_with_sample_html),
        ("Pattern Improvement Test", test_improved_contact_patterns),
        ("Real Website Test", test_contact_with_real_website),
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
    print(f"📊 CONTACT EXTRACTION TEST RESULTS")
    print("=" * 80)
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 Contact extraction tests completed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) had issues")

if __name__ == "__main__":
    asyncio.run(main()) 