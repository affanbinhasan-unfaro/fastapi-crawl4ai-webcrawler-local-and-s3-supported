"""
Pytest configuration and fixtures for the Web Scraper test suite.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_html():
    """Sample HTML with contact information for testing."""
    return """
    <html>
    <body>
        <h1>Contact Us</h1>
        <div class="contact-info">
            <p>Email us at: contact@example.com or info@test.org</p>
            <p>Call us: (555) 123-4567</p>
            <p>Phone: +1-800-555-0123</p>
            <div class="footer">
                <p>Support: support@company.com</p>
                <p>Sales: 555.987.6543</p>
            </div>
            <a href="mailto:direct@email.com">Direct Email</a>
            <a href="tel:+1-555-999-8888">Call Now</a>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_scraped_data():
    """Mock scraped data for testing storage functionality."""
    return {
        'metadata': {
            'scraping_timestamp': '2024-01-01T12:00:00Z',
            'source_url': 'https://test.com',
            'company_name': 'test_company',
            'extraction_method': 'crawl4AI_HTTP_BeautifulSoup',
            'total_pages_crawled': 1,
            'processing_time_seconds': 1.0
        },
        'data': {
            'text': [
                {
                    'content': 'Sample text content',
                    'page_url': 'https://test.com',
                    'confidence_score': 0.95,
                    'extraction_method': 'beautifulsoup_content_parsing'
                }
            ],
            'images': [],
            'contact': [
                {
                    'type': 'email',
                    'value': 'test@example.com',
                    'page_url': 'https://test.com',
                    'confidence_score': 0.95,
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


@pytest.fixture
def test_urls():
    """Common test URLs for various tests."""
    return {
        'simple': 'https://httpbin.org/html',
        'with_links': 'https://httpbin.org/links/3',
        'example': 'https://example.com'
    } 