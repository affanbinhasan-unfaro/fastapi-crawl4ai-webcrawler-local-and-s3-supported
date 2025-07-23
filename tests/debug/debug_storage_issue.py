#!/usr/bin/env python3
"""
Debug script to isolate the storage issue
"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def test_storage_directly():
    """Test storage service directly to isolate the issue"""
    print("🔍 Testing Storage Service Directly")
    print("=" * 50)
    
    try:
        from app.services.storage_service import storage_service
        
        # Create simple test data
        test_data = {
            'metadata': {
                'test': True,
                'timestamp': '2024-01-01T00:00:00Z'
            },
            'data': [
                {
                    'content': 'test content',
                    'page_url': 'https://example.com',
                    'confidence_score': 0.9
                }
            ],
            'data_type': 'text',
            'company_name': 'debug_test',
            'extraction_summary': {
                'total_items': 1,
                'has_content': True
            }
        }
        
        print("📊 Test data created successfully")
        
        # Try to upload using storage service
        print("💾 Attempting to upload test data...")
        
        result = await storage_service.upload_json_data(
            data=test_data,
            company_name='debug_test',
            data_type='text',
            file_name='debug_test_20240101_000000.json'
        )
        
        print(f"✅ Storage test successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_local_storage_directly():
    """Test local storage service directly"""
    print("\n🔍 Testing Local Storage Service Directly")
    print("=" * 50)
    
    try:
        from app.services.local_storage_service import local_storage_service
        
        test_data = {'test': 'simple data'}
        
        print("💾 Testing simple upload...")
        result = await local_storage_service.upload_json_data(
            data=test_data,
            company_name='simple_test',
            data_type='debug',
            file_name='simple_test.json'
        )
        
        print(f"✅ Local storage test successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Local storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_name_generation():
    """Test file name generation"""
    print("\n🔍 Testing File Name Generation")
    print("=" * 50)
    
    try:
        from app.utils.helpers import generate_file_name
        
        # Test different data types
        test_cases = [
            ('test_company', 'text'),
            ('test_company', 'images'),
            ('test_company', 'contact'),
            ('test_company', 'error')
        ]
        
        for company, data_type in test_cases:
            file_name = generate_file_name(company, data_type)
            print(f"✅ {data_type}: {file_name}")
            # Ensure it's a string
            assert isinstance(file_name, str), f"File name should be string, got {type(file_name)}"
        
        return True
        
    except Exception as e:
        print(f"❌ File name generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run debug tests"""
    print("🐛 STORAGE DEBUG TESTS")
    print("=" * 80)
    
    tests = [
        ("File Name Generation", test_file_name_generation),
        ("Local Storage Direct", test_local_storage_directly),
        ("Storage Service", test_storage_directly),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 40)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                success = await test_func()
            else:
                success = test_func()
                
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")

if __name__ == "__main__":
    asyncio.run(main()) 