#!/usr/bin/env python3
"""
Simple debug script for contact extraction
"""

import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Add project root directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_direct_extraction():
    """Test contact extraction directly without the class method"""
    print("🔍 Direct Contact Extraction Test")
    print("=" * 50)
    
    # Sample HTML with contacts
    sample_html = """
    <html>
    <body>
        <p>Email us at: contact@example.com</p>
        <p>Call us: (555) 123-4567</p>
    </body>
    </html>
    """
    
    soup = BeautifulSoup(sample_html, 'html.parser')
    all_text = soup.get_text()
    
    print(f"📄 Text extracted: '{all_text.strip()}'")
    
    # Test email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(email_pattern, all_text, re.IGNORECASE)
    print(f"📧 Emails found: {emails}")
    
    # Test phone extraction
    phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
    phones = re.findall(phone_pattern, all_text)
    print(f"📞 Phones found: {phones}")
    
    return len(emails) > 0 or len(phones) > 0

def test_with_scraper_method():
    """Test using the actual scraper method"""
    print("\n🔧 Testing with Scraper Method")
    print("=" * 50)
    
    try:
        from app.services.scraper import web_scraper
        from bs4 import BeautifulSoup
        
        # Enable debug mode
        web_scraper.debug = True
        
        sample_html = """
        <html>
        <body>
            <p>Email us at: contact@example.com</p>
            <p>Call us: (555) 123-4567</p>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        print("🧪 Calling _extract_contact_comprehensive...")
        contacts = web_scraper._extract_contact_comprehensive(soup, "https://example.com")
        
        print(f"📊 Contacts returned: {len(contacts)}")
        for contact in contacts:
            print(f"   - {contact['type']}: {contact['value']}")
        
        return len(contacts) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run debug tests"""
    print("🐛 CONTACT EXTRACTION DEBUG")
    print("=" * 60)
    
    # Test 1: Direct extraction
    direct_success = test_direct_extraction()
    print(f"✅ Direct test: {'PASSED' if direct_success else 'FAILED'}")
    
    # Test 2: Scraper method
    scraper_success = test_with_scraper_method()
    print(f"✅ Scraper method: {'PASSED' if scraper_success else 'FAILED'}")
    
    if direct_success and not scraper_success:
        print("\n⚠️  Issue is in the scraper method implementation!")
    elif not direct_success:
        print("\n⚠️  Issue is with the regex patterns!")
    else:
        print("\n🎉 Both tests passed!")

if __name__ == "__main__":
    main() 