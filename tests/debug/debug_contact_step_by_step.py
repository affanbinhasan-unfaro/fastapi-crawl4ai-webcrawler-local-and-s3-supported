#!/usr/bin/env python3
"""
Step-by-step debug script for contact extraction
"""

import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def debug_contact_method_step_by_step():
    """Debug the contact method step by step"""
    print("🔍 Step-by-Step Contact Method Debug")
    print("=" * 60)
    
    try:
        # Sample HTML
        sample_html = """
        <html>
        <body>
            <p>Email us at: contact@example.com</p>
            <p>Call us: (555) 123-4567</p>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(sample_html, 'html.parser')
        base_url = "https://example.com"
        
        print("📄 Step 1: Get text from soup")
        all_text = soup.get_text()
        print(f"   Text: '{all_text.strip()}'")
        
        print("\n📧 Step 2: Email extraction")
        contacts = []
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        emails = re.findall(email_pattern, all_text, re.IGNORECASE)
        print(f"   Raw emails found: {emails}")
        
        for email in set(emails)[:10]:
            if email and len(email) > 5:
                contact = {
                    'type': 'email',
                    'value': email.lower(),
                    'page_url': base_url,
                    'confidence_score': 0.95,
                    'extraction_method': 'regex_pattern_matching'
                }
                contacts.append(contact)
                print(f"   Added email: {contact}")
        
        print(f"\n📧 Contacts after email processing: {len(contacts)}")
        
        print("\n📞 Step 3: Phone extraction")
        phone_patterns = [
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            r'\+[1-9]\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',
        ]
        
        all_phone_matches = []
        for i, pattern in enumerate(phone_patterns):
            matches = re.findall(pattern, all_text)
            print(f"   Pattern {i+1}: {matches}")
            all_phone_matches.extend(matches)
        
        print(f"   All phone matches: {all_phone_matches}")
        
        processed_phones = set()
        for match in all_phone_matches[:10]:
            if isinstance(match, tuple):
                phone_str = ''.join(match)
            else:
                phone_str = str(match)
            
            phone_clean = re.sub(r'[^\d+]', '', phone_str)
            print(f"   Processing: {match} -> {phone_str} -> {phone_clean}")
            
            if len(phone_clean) >= 10 and phone_clean not in processed_phones:
                processed_phones.add(phone_clean)
                display_phone = phone_str if isinstance(match, str) else ''.join(match)
                
                contact = {
                    'type': 'phone',
                    'value': display_phone,
                    'page_url': base_url,
                    'confidence_score': 0.8,
                    'extraction_method': 'regex_pattern_matching'
                }
                contacts.append(contact)
                print(f"   Added phone: {contact}")
        
        print(f"\n📞 Contacts after phone processing: {len(contacts)}")
        
        print("\n🔧 Step 4: HTML element extraction")
        contact_selectors = [
            'a[href^="mailto:"]',
            'a[href^="tel:"]',
            '.contact',
            '.contact-info'
        ]
        
        for selector in contact_selectors:
            elements = soup.select(selector)
            print(f"   Selector '{selector}': {len(elements)} elements")
        
        print(f"\n📊 Step 5: Deduplication")
        seen_values = set()
        unique_contacts = []
        for contact in contacts:
            value_key = f"{contact['type']}:{contact['value']}"
            print(f"   Checking: {value_key}")
            if value_key not in seen_values:
                seen_values.add(value_key)
                unique_contacts.append(contact)
                print(f"   ✅ Added unique contact")
            else:
                print(f"   ⏭️ Skipped duplicate")
        
        print(f"\n🎯 Final Result: {len(unique_contacts)} unique contacts")
        for contact in unique_contacts:
            print(f"   - {contact['type']}: {contact['value']}")
        
        return len(unique_contacts) > 0
        
    except Exception as e:
        print(f"❌ Error in step-by-step debug: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_contact_method_step_by_step() 