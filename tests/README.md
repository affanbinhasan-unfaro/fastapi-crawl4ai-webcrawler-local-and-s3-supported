# 🧪 Web Scraper Test Suite

This directory contains a comprehensive test suite for the Web Scraper API, organized by test type and purpose.

## 📁 Directory Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── README.md                # This file
│
├── unit/                    # Unit Tests (Individual Components)
│   ├── __init__.py
│   ├── test_contact_extraction.py    # Contact extraction logic tests
│   ├── test_crawler.py               # Crawler component tests  
│   ├── test_fixes.py                 # Bug fix verification tests
│   └── test_storage.py               # Storage functionality tests
│
├── integration/             # Integration Tests (End-to-End Workflows)
│   ├── __init__.py
│   ├── test_api_integration.py       # Complete API workflow tests
│   ├── test_contact_with_real_website.py  # Real website contact testing
│   ├── test_scraper_integration.py   # Scraper integration tests
│   ├── test_simplified_api.py        # Simplified API tests
│   └── test_updated_scraper.py       # Updated scraper validation
│
├── debug/                   # Debug Scripts (Troubleshooting Tools)  
│   ├── __init__.py
│   ├── debug_contact_simple.py       # Simple contact debug
│   ├── debug_contact_step_by_step.py # Detailed contact analysis
│   ├── debug_crawler.py              # Crawler diagnostics
│   ├── debug_links.py                # Link extraction debugging
│   └── debug_storage_issue.py        # Storage problem analysis
│
└── api/                     # API-Specific Tests (Future)
    └── __init__.py
```

## 🏃‍♂️ Running Tests

### All Tests
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app
```

### Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only  
pytest tests/integration/

# Specific test file
pytest tests/unit/test_contact_extraction.py

# Specific test function
pytest tests/unit/test_contact_extraction.py::test_contact_extraction_with_sample_html
```

### Debug Scripts
```bash
# Run debug scripts directly (not with pytest)
python tests/debug/debug_contact_simple.py
python tests/debug/debug_storage_issue.py
```

## 📋 Test Categories

### 🔧 Unit Tests (`tests/unit/`)
Test individual components in isolation:

- **`test_contact_extraction.py`**: Tests contact extraction patterns and logic
- **`test_crawler.py`**: Tests crawler components and HTTP functionality
- **`test_fixes.py`**: Validates bug fixes and improvements
- **`test_storage.py`**: Tests storage operations and data formatting

### 🔄 Integration Tests (`tests/integration/`)
Test complete workflows and component interactions:

- **`test_api_integration.py`**: End-to-end API workflow testing
- **`test_contact_with_real_website.py`**: Real website contact extraction
- **`test_scraper_integration.py`**: Scraper service integration
- **`test_simplified_api.py`**: Simplified API validation
- **`test_updated_scraper.py`**: Updated scraper verification

### 🐛 Debug Scripts (`tests/debug/`)
Diagnostic tools for troubleshooting:

- **`debug_contact_simple.py`**: Quick contact extraction diagnosis
- **`debug_contact_step_by_step.py`**: Detailed contact extraction analysis  
- **`debug_crawler.py`**: Crawler behavior diagnostics
- **`debug_links.py`**: Link extraction debugging
- **`debug_storage_issue.py`**: Storage problem investigation

## 🎯 Test Goals

### Unit Tests
- ✅ Verify individual functions work correctly
- ✅ Test edge cases and error handling
- ✅ Validate data extraction patterns
- ✅ Ensure storage format compliance

### Integration Tests  
- ✅ Test complete scraping workflows
- ✅ Verify API endpoint functionality
- ✅ Validate data flow from scraping to storage
- ✅ Test real-world scenarios

### Debug Scripts
- ✅ Identify root causes of issues
- ✅ Provide detailed diagnostic information
- ✅ Enable step-by-step troubleshooting
- ✅ Validate fixes and improvements

## 📝 Writing New Tests

### Unit Test Template
```python
#!/usr/bin/env python3
"""
Test description
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_function_name():
    """Test description"""
    # Arrange
    # Act  
    # Assert
    pass

async def test_async_function():
    """Async test description"""
    # Test async functionality
    pass
```

### Integration Test Template
```python
#!/usr/bin/env python3
"""
Integration test description
"""

import asyncio
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete workflow"""
    # Test end-to-end functionality
    pass
```

## 🔧 Fixtures Available

From `conftest.py`:
- **`sample_html`**: HTML with contact information
- **`mock_scraped_data`**: Mock scraped data structure
- **`test_urls`**: Common test URLs
- **`event_loop`**: Async event loop for testing

## 📊 Test Status

- ✅ **Unit Tests**: Contact extraction, storage, crawler components
- ✅ **Integration Tests**: API workflows, scraper integration  
- ✅ **Debug Scripts**: Comprehensive diagnostic tools
- 🚧 **API Tests**: Future endpoint-specific testing

## 🚀 CI/CD Integration

For continuous integration, run:
```bash
# Quick test suite (unit tests only)
pytest tests/unit/ -v

# Full test suite (all tests)  
pytest tests/ -v --cov=app --cov-report=html

# Performance tests (integration tests)
pytest tests/integration/ -v --durations=10
```

## 📈 Coverage Goals

- **Unit Tests**: >90% code coverage
- **Integration Tests**: >80% workflow coverage
- **Debug Scripts**: Diagnostic completeness
- **Overall**: >85% project coverage

## 🎯 Best Practices

1. **Write tests first** (TDD approach)
2. **Keep tests isolated** (no dependencies between tests)
3. **Use descriptive names** (test_should_extract_contacts_from_sample_html)
4. **Test edge cases** (empty data, malformed input, network errors)
5. **Mock external dependencies** (HTTP requests, file operations)
6. **Keep tests fast** (<1s per unit test, <10s per integration test)

---

**📞 Questions or Issues?** 
Check the debug scripts first, then review test failures for detailed diagnostics. 