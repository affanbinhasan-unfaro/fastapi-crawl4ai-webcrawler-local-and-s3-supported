"""
crawl4AI integration service for web scraping with improved HTTP-only approach.
"""
import asyncio
import time
import re
import json
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from bs4 import BeautifulSoup
import httpx
from app.core.config import settings
from app.core.exceptions import ScrapingError, TimeoutError
from app.utils.logger import logger
from app.utils.helpers import retry_async, extract_domain_from_url


class WebScraper:
    """Improved crawl4AI-based web scraper service using HTTP-only approach with BeautifulSoup."""
    
    def __init__(self):
        """Initialize the scraper."""
        self.max_depth = settings.max_crawl_depth
        self.timeout = settings.crawl_timeout
        self.max_concurrent = settings.max_concurrent_requests
        self.crawled_urls: Set[str] = set()
        self.crawl_data: Dict[str, Any] = {}
        self.base_domain = ""
        self.debug = True
        self.reset_crawl_data()
    
    def reset_crawl_data(self):
        """Reset crawl data structure."""
        self.crawl_data = {
            'text': [],
            'images': [],
            'contact': [],
            'products': [],
            'social_media': [],
            'metadata': [],
            'raw_html': {},
            'sitemap': {
                'crawl_structure': {},
                'coverage_summary': {
                    'total_pages': 0,
                    'pages_with_text': 0,
                    'pages_with_images': 0,
                    'pages_with_contact': 0,
                    'pages_with_products': 0,
                    'pages_with_social_media': 0
                }
            }
        }
    
    async def scrape_website(
        self,
        url: str,
        company_name: str,
        max_depth: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Scrape website using improved HTTP-only crawl4AI with comprehensive data extraction.
        
        Args:
            url: Website URL to scrape
            company_name: Company name
            max_depth: Maximum crawl depth (overrides config)
            
        Returns:
            Scraped data dictionary with all data types
            
        Raises:
            ScrapingError: If scraping fails
            TimeoutError: If scraping times out
        """
        start_time = time.time()
        
        try:
            # Reset state for new scraping session
            self.crawled_urls.clear()
            self.reset_crawl_data()
            self.base_domain = extract_domain_from_url(url)
            
            # Use provided max_depth or default
            crawl_depth = max_depth or self.max_depth
            
            logger.info(f"Starting improved HTTP-only scrape of {url} with depth {crawl_depth}")
            
            # Start comprehensive crawling using HTTP-only approach
            await self._crawl_website_comprehensive(url, crawl_depth, company_name)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update coverage summary
            self._update_coverage_summary()
            
            logger.info(
                f"Completed improved HTTP scraping of {url}. "
                f"Pages crawled: {len(self.crawled_urls)}, "
                f"Time: {processing_time:.2f}s"
            )
            
            return {
                'metadata': {
                    'scraping_timestamp': self._get_timestamp(),
                    'source_url': url,
                    'company_name': company_name,
                    'extraction_method': 'crawl4AI_HTTP_BeautifulSoup',
                    'crawl_depth': crawl_depth,
                    'total_pages_crawled': len(self.crawled_urls),
                    'processing_time_seconds': round(processing_time, 2),
                    'base_domain': self.base_domain
                },
                'data': {
                    'text': self.crawl_data['text'],
                    'images': self.crawl_data['images'],
                    'contact': self.crawl_data['contact'],
                    'products': self.crawl_data['products'],
                    'social_media': self.crawl_data['social_media'],
                    'metadata': self.crawl_data['metadata']
                },
                'raw_html': self.crawl_data['raw_html'],
                'sitemap': self.crawl_data['sitemap']
            }
            
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Scraping timed out after {self.timeout} seconds",
                self.timeout
            )
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {str(e)}")
            raise ScrapingError(
                f"Failed to scrape {url}: {str(e)}",
                url
            )
    
    async def _crawl_website_comprehensive(
        self,
        url: str,
        max_depth: int,
        company_name: str,
        current_depth: int = 0
    ) -> None:
        """
        Comprehensively crawl website using improved HTTP-only crawl4ai with BeautifulSoup.
        """
        if current_depth > max_depth or url in self.crawled_urls:
            return
        
        # Normalize URL
        normalized_url = self._normalize_url(url)
        if normalized_url in self.crawled_urls:
            return
            
        # Check if URL belongs to same domain
        if extract_domain_from_url(normalized_url) != self.base_domain:
            return
            
        self.crawled_urls.add(normalized_url)
        logger.info(f"HTTP crawling {normalized_url} at depth {current_depth}")
        
        html_content = ""
        text_content = ""
        
        try:
            # Use improved HTTP-only crawl4ai approach
            html_content, text_content = await self._crawl_with_http_crawl4ai(normalized_url)
        except Exception as e:
            logger.warning(f"HTTP crawl4ai failed for {normalized_url}: {e}")
            try:
                # Fallback to httpx if needed
                html_content, text_content = await self._crawl_with_httpx(normalized_url)
            except Exception as e2:
                logger.warning(f"httpx fallback failed for {normalized_url}: {e2}")
                return
        
        if html_content:
            # Extract all data from the page using BeautifulSoup
            await self._extract_comprehensive_data(
                normalized_url, 
                html_content, 
                text_content,
                current_depth
            )
            
            # Find and crawl subpages using BeautifulSoup if not at max depth
            if current_depth < max_depth:
                links = self._extract_all_links_with_beautifulsoup(html_content, normalized_url)
                await self._crawl_subpages(
                    links, 
                    max_depth, 
                    company_name, 
                    current_depth + 1
                )
    
    async def _crawl_with_http_crawl4ai(self, url: str) -> tuple[str, str]:
        """Crawl with improved HTTP-only crawl4ai approach."""
        try:
            # Simple extraction schema for basic content
            extraction_schema = {
                "name": "BasicExtractor",
                "baseSelector": "body",
                "fields": [
                    {"name": "title", "selector": "title", "type": "text"},
                    {"name": "meta_description", "selector": "meta[name='description']", "type": "attribute", "attribute": "content"},
                    {"name": "headings", "selector": "h1, h2, h3", "type": "text", "multiple": True}
                ]
            }
            
            # Configure HTTP-only crawler
            run_config = CrawlerRunConfig(
                word_count_threshold=1,
                extraction_strategy=JsonCssExtractionStrategy(extraction_schema),
                cache_mode="bypass",
                verbose=False,
                page_timeout=min(self.timeout * 1000, 30000),
                wait_until="domcontentloaded"
            )
            
            # Create HTTP crawler strategy
            http_strategy = AsyncHTTPCrawlerStrategy()
            
            async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
                result = await crawler.arun(url=url, config=run_config)
                
                if result.success and hasattr(result, 'html') and result.html:
                    html_content = result.cleaned_html if hasattr(result, 'cleaned_html') else result.html
                    markdown_content = str(result.markdown) if hasattr(result, 'markdown') and result.markdown else ''
                    return html_content, markdown_content
                else:
                    raise Exception(f"HTTP crawl4ai failed: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")
                    
        except Exception as e:
            raise Exception(f"HTTP crawl4ai error: {str(e)}")
    
    async def _crawl_with_httpx(self, url: str) -> tuple[str, str]:
        """Fallback crawling with httpx (unchanged for compatibility)."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                html_content = response.text
                # Extract text content from HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                text_content = soup.get_text(separator=' ', strip=True)
                
                return html_content, text_content
                
        except Exception as e:
            raise Exception(f"httpx error: {str(e)}")
    
    def _extract_all_links_with_beautifulsoup(self, html_content: str, base_url: str) -> List[str]:
        """Extract all links using BeautifulSoup for reliable parsing (improved version)."""
        links = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            a_tags = soup.find_all('a', href=True)
            
            if self.debug:
                logger.debug(f"BeautifulSoup found {len(a_tags)} <a> tags on {base_url}")
            
            for a_tag in a_tags:
                href = a_tag.get('href', '').strip()
                
                if not href or href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                    continue
                
                # Normalize URL
                if href.startswith('//'):
                    base_parsed = urlparse(base_url)
                    full_url = f"{base_parsed.scheme}:{href}"
                elif href.startswith('/'):
                    base_parsed = urlparse(base_url)
                    full_url = f"{base_parsed.scheme}://{base_parsed.netloc}{href}"
                elif not href.startswith(('http://', 'https://')):
                    full_url = urljoin(base_url, href)
                else:
                    full_url = href
                
                # Remove fragments
                if '#' in full_url:
                    full_url = full_url.split('#')[0]
                
                # Only include links from the same domain
                if extract_domain_from_url(full_url) == self.base_domain:
                    normalized_url = self._normalize_url(full_url)
                    if normalized_url not in links:
                        links.append(normalized_url)
                        
        except Exception as e:
            logger.warning(f"Failed to extract links from {base_url}: {e}")
        
        return links
    
    async def _extract_comprehensive_data(
        self,
        url: str,
        html_content: str,
        text_content: str,
        depth: int
    ) -> None:
        """Extract comprehensive data using BeautifulSoup with improved parsing."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Store raw HTML
            self.crawl_data['raw_html'][url] = html_content
            
            # Extract all data types using BeautifulSoup
            text_data = self._extract_text_comprehensive(soup, text_content, url)
            image_data = self._extract_images_comprehensive(soup, url)
            contact_data = self._extract_contact_comprehensive(soup, url)
            product_data = self._extract_products_comprehensive(soup, url)
            social_data = self._extract_social_media_comprehensive(soup, url)
            metadata = self._extract_metadata_comprehensive(soup, url, depth)
            
            # Add to crawl data
            self.crawl_data['text'].extend(text_data)
            self.crawl_data['images'].extend(image_data)
            self.crawl_data['contact'].extend(contact_data)
            self.crawl_data['products'].extend(product_data)
            self.crawl_data['social_media'].extend(social_data)
            self.crawl_data['metadata'].append(metadata)
            
            # Update sitemap
            links_found = self._extract_all_links_with_beautifulsoup(html_content, url)
            self.crawl_data['sitemap']['crawl_structure'][url] = {
                'depth': depth,
                'links_found': links_found[:10],  # Limit for storage
                'data_extracted': [
                    'text' if text_data else None,
                    'images' if image_data else None,
                    'contact' if contact_data else None,
                    'products' if product_data else None,
                    'social_media' if social_data else None
                ]
            }
            
            logger.info(f"Extracted data from {url}: {len(text_data)} text, {len(image_data)} images, "
                       f"{len(contact_data)} contacts, {len(product_data)} products, {len(social_data)} social")
                       
        except Exception as e:
            logger.error(f"Failed to extract comprehensive data from {url}: {e}")

    def _extract_text_comprehensive(self, soup: BeautifulSoup, text_content: str, base_url: str) -> List[Dict[str, Any]]:
        """Extract comprehensive text content using improved parsing."""
        text_items = []
        
        try:
            # Extract main content areas
            content_selectors = [
                'main', 'article', '.content', '.main-content', 
                '.entry-content', '.post-content', '#content'
            ]
            
            main_content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    main_content = content_elem.get_text(separator=' ', strip=True)
                    break
            
            # If no main content found, use body text
            if not main_content:
                main_content = text_content
            
            # Clean and process text
            if main_content and len(main_content.strip()) > 50:
                # Split into paragraphs
                paragraphs = [p.strip() for p in main_content.split('\n') if len(p.strip()) > 20]
                
                for paragraph in paragraphs[:20]:  # Limit paragraphs
                    text_items.append({
                        'content': paragraph[:1000],  # Limit length
                        'page_url': base_url,
                        'confidence_score': 0.85,
                        'extraction_method': 'beautifulsoup_content_parsing'
                    })
            
            # Extract headings separately
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings[:10]:
                heading_text = heading.get_text(strip=True)
                if heading_text and len(heading_text) > 3:
                    text_items.append({
                        'content': f"[{heading.name.upper()}] {heading_text}",
                        'page_url': base_url,
                        'confidence_score': 0.95,
                        'extraction_method': 'beautifulsoup_heading_extraction'
                    })
                    
        except Exception as e:
            logger.debug(f"Error extracting text from {base_url}: {e}")
        
        return text_items

    def _extract_images_comprehensive(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract comprehensive image data using BeautifulSoup."""
        images = []
        
        try:
            img_tags = soup.find_all('img', src=True)
            
            for img in img_tags[:20]:  # Limit images
                src = img.get('src', '').strip()
                alt = img.get('alt', '').strip()
                
                if src:
                    # Normalize image URL
                    if src.startswith('//'):
                        base_parsed = urlparse(base_url)
                        img_url = f"{base_parsed.scheme}:{src}"
                    elif src.startswith('/'):
                        base_parsed = urlparse(base_url)
                        img_url = f"{base_parsed.scheme}://{base_parsed.netloc}{src}"
                    elif not src.startswith(('http://', 'https://')):
                        img_url = urljoin(base_url, src)
                    else:
                        img_url = src
                    
                    # Extract dimensions if available
                    width = img.get('width')
                    height = img.get('height')
                    
                    images.append({
                        'url': img_url,
                        'alt_text': alt,
                        'dimensions': {
                            'width': int(width) if width and width.isdigit() else None,
                            'height': int(height) if height and height.isdigit() else None
                        },
                        'page_url': base_url,
                        'confidence_score': 0.9,
                        'extraction_method': 'beautifulsoup_img_parsing'
                    })
        
        except Exception as e:
            logger.debug(f"Error extracting images from {base_url}: {e}")
        
        return images

    def _extract_contact_comprehensive(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract comprehensive contact information using BeautifulSoup."""
        contacts = []
        unique_contacts = []  # Initialize here to avoid scope issues
        
        try:
            # Get all text content for pattern matching
            all_text = soup.get_text()
            
            if self.debug:
                logger.debug(f"Extracting contacts from text: {all_text[:200]}...")
            
            # Improved email pattern - more comprehensive
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            emails = re.findall(email_pattern, all_text, re.IGNORECASE)
            
            if self.debug:
                logger.debug(f"Found {len(emails)} emails: {emails}")
            
            for email in list(set(emails))[:10]:  # Convert set to list before slicing
                if email and len(email) > 5:  # Basic validation
                    contacts.append({
                        'type': 'email',
                        'value': email.lower(),
                        'page_url': base_url,
                        'confidence_score': 0.95,
                        'extraction_method': 'regex_pattern_matching'
                    })
            
            # Improved phone patterns - more comprehensive
            phone_patterns = [
                # US/Canada patterns
                r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                # International patterns  
                r'\+[1-9]\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
                # General patterns
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
                # Extended patterns
                r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',
            ]
            
            all_phone_matches = []
            for pattern in phone_patterns:
                matches = re.findall(pattern, all_text)
                all_phone_matches.extend(matches)
            
            if self.debug:
                logger.debug(f"Found phone matches: {all_phone_matches}")
            
            # Process phone matches
            processed_phones = set()
            for match in all_phone_matches[:10]:  # Limit phone extractions
                if isinstance(match, tuple):
                    # For patterns with groups
                    phone_str = ''.join(match)
                else:
                    # For patterns without groups
                    phone_str = str(match)
                
                # Clean phone number
                phone_clean = re.sub(r'[^\d+]', '', phone_str)
                
                # Validate phone length (minimum 10 digits for valid phone)
                if len(phone_clean) >= 10 and phone_clean not in processed_phones:
                    processed_phones.add(phone_clean)
                    
                    # Format for display
                    display_phone = phone_str if isinstance(match, str) else ''.join(match)
                    
                    contacts.append({
                        'type': 'phone',
                        'value': display_phone,
                        'page_url': base_url,
                        'confidence_score': 0.8,
                        'extraction_method': 'regex_pattern_matching'
                    })
            
            # Also look for contact info in specific HTML elements
            contact_selectors = [
                'a[href^="mailto:"]',
                'a[href^="tel:"]',
                '.contact',
                '.contact-info',
                '.email',
                '.phone',
                '[class*="contact"]',
                '[id*="contact"]'
            ]
            
            for selector in contact_selectors:
                elements = soup.select(selector)
                for element in elements:
                    if element.name == 'a':
                        href = element.get('href', '')
                        if href.startswith('mailto:'):
                            email = href.replace('mailto:', '').strip()
                            if email and '@' in email:
                                contacts.append({
                                    'type': 'email',
                                    'value': email.lower(),
                                    'page_url': base_url,
                                    'confidence_score': 0.98,
                                    'extraction_method': 'html_mailto_link'
                                })
                        elif href.startswith('tel:'):
                            phone = href.replace('tel:', '').strip()
                            if phone and len(phone) >= 10:
                                contacts.append({
                                    'type': 'phone',
                                    'value': phone,
                                    'page_url': base_url,
                                    'confidence_score': 0.98,
                                    'extraction_method': 'html_tel_link'
                                })
                    else:
                        # Extract from element text
                        element_text = element.get_text()
                        # Quick email check
                        element_emails = re.findall(email_pattern, element_text, re.IGNORECASE)
                        for email in element_emails[:3]:
                            if email and len(email) > 5:
                                contacts.append({
                                    'type': 'email',
                                    'value': email.lower(),
                                    'page_url': base_url,
                                    'confidence_score': 0.90,
                                    'extraction_method': 'html_element_text'
                                })
            
            # Remove duplicates based on value
            seen_values = set()
            unique_contacts = []  # Reset here for proper processing
            for contact in contacts:
                value_key = f"{contact['type']}:{contact['value']}"
                if value_key not in seen_values:
                    seen_values.add(value_key)
                    unique_contacts.append(contact)
            
            if self.debug:
                logger.debug(f"Total unique contacts extracted: {len(unique_contacts)}")
                
        except Exception as e:
            logger.debug(f"Error extracting contact info from {base_url}: {e}")
        
        return unique_contacts

    def _extract_products_comprehensive(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract comprehensive product information using BeautifulSoup."""
        products = []
        
        try:
            # Product-related selectors
            product_selectors = [
                '.product', '.item', '.listing', '.card',
                '[class*="product"]', '[class*="item"]'
            ]
            
            for selector in product_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements[:10]:  # Limit products
                        product_name = ""
                        product_price = ""
                        product_description = ""
                        
                        # Extract product name from various elements
                        name_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '[class*="title"]', '[class*="name"]']
                        for name_sel in name_selectors:
                            name_elem = element.select_one(name_sel)
                            if name_elem:
                                product_name = name_elem.get_text(strip=True)
                                break
                        
                        # Extract price using regex
                        element_text = element.get_text()
                        price_pattern = r'[\$£€¥]\s?\d+(?:[\.,]\d{2})?'
                        price_match = re.search(price_pattern, element_text)
                        if price_match:
                            product_price = price_match.group()
                        
                        # Extract description
                        desc_selectors = ['p', '.description', '.summary', '[class*="desc"]']
                        for desc_sel in desc_selectors:
                            desc_elem = element.select_one(desc_sel)
                            if desc_elem:
                                product_description = desc_elem.get_text(strip=True)[:200]
                                break
                        
                        if product_name and len(product_name) > 2:
                            products.append({
                                'name': product_name,
                                'price': product_price,
                                'description': product_description,
                                'page_url': base_url,
                                'confidence_score': 0.75,
                                'extraction_method': 'beautifulsoup_css_selector_parsing'
                            })
                except Exception as e:
                    logger.debug(f"Error extracting products with selector {selector}: {e}")
                    
        except Exception as e:
            logger.debug(f"Error extracting products from {base_url}: {e}")
        
        return products

    def _extract_social_media_comprehensive(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract comprehensive social media links using BeautifulSoup."""
        social_media = []
        
        try:
            social_platforms = {
                'facebook.com': 'Facebook',
                'twitter.com': 'Twitter',
                'x.com': 'X (Twitter)',
                'linkedin.com': 'LinkedIn',
                'instagram.com': 'Instagram',
                'youtube.com': 'YouTube',
                'tiktok.com': 'TikTok',
                'pinterest.com': 'Pinterest',
                'snapchat.com': 'Snapchat',
                'github.com': 'GitHub'
            }
            
            # Find all links
            links = soup.find_all('a', href=True)
            found_platforms = set()
            
            for link in links:
                href = link['href']
                link_text = link.get_text(strip=True)
                
                for platform_domain, platform_name in social_platforms.items():
                    if platform_domain in href and platform_name not in found_platforms:
                        social_media.append({
                            'platform': platform_name,
                            'url': href,
                            'link_text': link_text,
                            'page_url': base_url,
                            'confidence_score': 0.95,
                            'extraction_method': 'beautifulsoup_domain_matching'
                        })
                        found_platforms.add(platform_name)
                        break
                        
        except Exception as e:
            logger.debug(f"Error extracting social media from {base_url}: {e}")
        
        return social_media

    def _extract_metadata_comprehensive(self, soup: BeautifulSoup, url: str, depth: int) -> Dict[str, Any]:
        """Extract comprehensive page metadata using BeautifulSoup."""
        metadata = {
            'page_url': url,
            'depth': depth,
            'title': self._extract_page_title(soup),
            'description': '',
            'keywords': '',
            'og_title': '',
            'og_description': '',
            'og_image': '',
            'canonical_url': '',
            'language': soup.get('lang', ''),
            'charset': '',
            'robots': '',
            'extraction_method': 'beautifulsoup_meta_parsing'
        }
        
        try:
            # Extract meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '').lower()
                property_attr = meta.get('property', '').lower()
                content = meta.get('content', '')
                
                if name == 'description':
                    metadata['description'] = content
                elif name == 'keywords':
                    metadata['keywords'] = content
                elif name == 'robots':
                    metadata['robots'] = content
                elif property_attr == 'og:title':
                    metadata['og_title'] = content
                elif property_attr == 'og:description':
                    metadata['og_description'] = content
                elif property_attr == 'og:image':
                    metadata['og_image'] = content
                elif meta.get('charset'):
                    metadata['charset'] = meta.get('charset')
            
            # Extract canonical URL
            canonical = soup.find('link', rel='canonical')
            if canonical:
                metadata['canonical_url'] = canonical.get('href', '')
                
        except Exception as e:
            logger.debug(f"Error extracting metadata from {url}: {e}")
        
        return metadata

    async def _crawl_subpages(
        self,
        links: List[str],
        max_depth: int,
        company_name: str,
        current_depth: int
    ) -> None:
        """Crawl subpages with improved concurrency control."""
        if not links or current_depth > max_depth:
            return
        
        # Filter out already crawled URLs
        new_links = [link for link in links if link not in self.crawled_urls]
        
        # Limit concurrent requests to prevent overwhelming
        semaphore = asyncio.Semaphore(min(self.max_concurrent, 3))
        
        async def crawl_with_semaphore(link):
            async with semaphore:
                await asyncio.sleep(0.5)  # Rate limiting
                await self._crawl_website_comprehensive(
                    link, max_depth, company_name, current_depth
                )
        
        # Process links in smaller batches
        batch_size = min(10, len(new_links))
        tasks = [crawl_with_semaphore(link) for link in new_links[:batch_size]]
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and unnecessary parameters."""
        try:
            parsed = urlparse(url)
            # Remove fragment and normalize
            normalized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path.rstrip('/') or '/',
                parsed.params,
                parsed.query,
                ''  # Remove fragment
            ))
            return normalized
        except Exception:
            return url
    
    def _extract_page_title(self, soup: BeautifulSoup) -> str:
        """Extract page title using BeautifulSoup."""
        try:
            title_tag = soup.find('title')
            return title_tag.get_text(strip=True) if title_tag else ''
        except Exception:
            return ''
    
    def _update_coverage_summary(self):
        """Update coverage summary statistics."""
        try:
            coverage = self.crawl_data['sitemap']['coverage_summary']
            coverage['total_pages'] = len(self.crawled_urls)
            coverage['pages_with_text'] = len([item for item in self.crawl_data['text'] if item])
            coverage['pages_with_images'] = len([item for item in self.crawl_data['images'] if item])
            coverage['pages_with_contact'] = len([item for item in self.crawl_data['contact'] if item])
            coverage['pages_with_products'] = len([item for item in self.crawl_data['products'] if item])
            coverage['pages_with_social_media'] = len([item for item in self.crawl_data['social_media'] if item])
        except Exception as e:
            logger.debug(f"Error updating coverage summary: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


# Create a global instance for the application
web_scraper = WebScraper() 