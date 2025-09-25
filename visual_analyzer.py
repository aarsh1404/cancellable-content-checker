"""
Enhanced visual content analyzer for URLs
Includes screenshot capture and visual content extraction
"""

import os
import io
import base64
import requests
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
from PIL import Image
import streamlit as st

# Optional imports for advanced features
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class VisualURLAnalyzer:
    """Enhanced URL analyzer with visual content extraction capabilities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize browser options
        self.chrome_options = None
        if SELENIUM_AVAILABLE:
            self.chrome_options = Options()
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--no-sandbox')
            self.chrome_options.add_argument('--disable-dev-shm-usage')
            self.chrome_options.add_argument('--window-size=1920,1080')
            self.chrome_options.add_argument('--disable-gpu')
    
    def _extract_content_with_playwright(self, url: str) -> Dict:
        """Extract content using Playwright for JavaScript-heavy sites"""
        try:
            if not PLAYWRIGHT_AVAILABLE:
                return {'text_content': '', 'error': 'Playwright not available'}
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set realistic headers
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                })
                
                try:
                    page.goto(url, timeout=30000)
                    
                    # Wait for content to load
                    try:
                        page.wait_for_load_state('networkidle', timeout=15000)
                    except:
                        page.wait_for_load_state('domcontentloaded', timeout=10000)
                    
                    # Additional wait for dynamic content
                    page.wait_for_timeout(5000)
                    
                    # Extract text content
                    text_content = page.evaluate("""
                        () => {
                            // Remove unwanted elements
                            const unwanted = document.querySelectorAll('script, style, nav, footer, header, aside, .ad, .advertisement');
                            unwanted.forEach(el => el.remove());
                            
                            // Try to find main content
                            const mainSelectors = ['main', 'article', '.content', '#content', '.main-content', 
                                                 '.post-content', '.entry-content', '.article-content', '.post-body',
                                                 '[data-testid="tweet"]', '.tweet', '.post', '.status'];
                            
                            let mainContent = null;
                            for (const selector of mainSelectors) {
                                mainContent = document.querySelector(selector);
                                if (mainContent) break;
                            }
                            
                            if (!mainContent) {
                                mainContent = document.body;
                            }
                            
                            return mainContent.innerText || mainContent.textContent || '';
                        }
                    """)
                    
                    # Extract images
                    images = page.evaluate("""
                        () => {
                            const imgs = Array.from(document.querySelectorAll('img')).slice(0, 10);
                            return imgs.map(img => ({
                                src: img.src,
                                alt: img.alt || '',
                                title: img.title || '',
                                description: (img.alt ? 'Alt: ' + img.alt : '') + (img.title ? '; Title: ' + img.title : '')
                            })).filter(img => img.src);
                        }
                    """)
                    
                    # Extract metadata
                    metadata = page.evaluate("""
                        () => {
                            const meta = {};
                            const titleEl = document.querySelector('title');
                            if (titleEl) meta.title = titleEl.textContent;
                            
                            const descEl = document.querySelector('meta[name="description"]');
                            if (descEl) meta.description = descEl.content;
                            
                            const ogTitle = document.querySelector('meta[property="og:title"]');
                            if (ogTitle) meta.og_title = ogTitle.content;
                            
                            const ogDesc = document.querySelector('meta[property="og:description"]');
                            if (ogDesc) meta.og_description = ogDesc.content;
                            
                            return meta;
                        }
                    """)
                    
                    return {
                        'text_content': text_content.strip()[:4000] if text_content else '',
                        'images': images,
                        'metadata': metadata,
                        'error': None
                    }
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            return {
                'text_content': '',
                'images': [],
                'metadata': {},
                'error': f"Playwright extraction failed: {str(e)}"
            }
    
    def analyze_url_enhanced(self, url: str) -> Dict:
        """
        Enhanced URL analysis with visual content extraction
        
        Returns:
            Dictionary containing text content, visual elements, and metadata
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format")
            
            result = {
                'url': url,
                'text_content': '',
                'visual_elements': [],
                'screenshot': None,
                'metadata': {},
                'images': [],
                'error': None
            }
            
            # Try Playwright first for JavaScript-heavy sites (like X.com, Instagram, etc.)
            if any(domain in url.lower() for domain in ['x.com', 'twitter.com', 'instagram.com', 'tiktok.com', 'linkedin.com']):
                st.info("🔍 Detected JavaScript-heavy site, using advanced extraction...")
                playwright_result = self._extract_content_with_playwright(url)
                
                if playwright_result.get('text_content'):
                    result['text_content'] = playwright_result['text_content']
                    result['images'] = playwright_result.get('images', [])
                    result['metadata'].update(playwright_result.get('metadata', {}))
                else:
                    result['error'] = playwright_result.get('error', 'Playwright extraction failed')
                    return result
            else:
                # Get basic page content for regular sites
                try:
                    response = self.session.get(url, timeout=15)
                    response.raise_for_status()
                    result['text_content'] = self._extract_text_from_html(response.text, url)
                except Exception as e:
                    result['error'] = f"Failed to fetch basic content: {str(e)}"
                    return result
            
            # Extract images and visual elements (only for non-JS sites)
            if not any(domain in url.lower() for domain in ['x.com', 'twitter.com', 'instagram.com', 'tiktok.com', 'linkedin.com']):
                try:
                    response = self.session.get(url, timeout=15)
                    response.raise_for_status()
                    result['images'] = self._extract_images(response.text, url)
                    result['visual_elements'] = self._extract_visual_elements(response.text)
                except Exception as e:
                    st.warning(f"Visual extraction warning: {str(e)}")
            
            # Try to capture screenshot
            try:
                if SELENIUM_AVAILABLE:
                    result['screenshot'] = self._capture_screenshot_selenium(url)
                elif PLAYWRIGHT_AVAILABLE:
                    result['screenshot'] = self._capture_screenshot_playwright(url)
                else:
                    result['screenshot'] = self._capture_screenshot_fallback(url)
            except Exception as e:
                st.warning(f"Screenshot capture warning: {str(e)}")
            
            # Extract metadata (only for non-JS sites, JS sites already have metadata)
            if not any(domain in url.lower() for domain in ['x.com', 'twitter.com', 'instagram.com', 'tiktok.com', 'linkedin.com']):
                try:
                    response = self.session.get(url, timeout=15)
                    response.raise_for_status()
                    result['metadata'] = self._extract_metadata(response.text, url)
                except Exception as e:
                    st.warning(f"Metadata extraction warning: {str(e)}")
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'text_content': '',
                'visual_elements': [],
                'screenshot': None,
                'metadata': {},
                'images': [],
                'error': f"Analysis failed: {str(e)}"
            }
    
    def _extract_text_from_html(self, html_content: str, base_url: str) -> str:
        """Extract clean text content from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Find main content
            main_content = None
            main_selectors = [
                'main', 'article', '.content', '#content', '.main-content',
                '.post-content', '.entry-content', '.article-content', '.post-body'
            ]
            
            for selector in main_selectors:
                element = soup.select_one(selector)
                if element:
                    main_content = element
                    break
            
            if not main_content:
                main_content = soup.find('body') or soup
            
            # Extract text
            text = main_content.get_text()
            
            # Clean up
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:4000] if len(text) > 4000 else text
            
        except Exception as e:
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def _extract_images(self, html_content: str, base_url: str) -> List[Dict]:
        """Extract images and their metadata from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            images = []
            img_tags = soup.find_all('img')
            
            for img in img_tags[:10]:  # Limit to first 10 images
                img_data = {
                    'src': '',
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'description': ''
                }
                
                # Handle relative URLs
                src = img.get('src', '')
                if src:
                    if src.startswith('//'):
                        img_data['src'] = 'https:' + src
                    elif src.startswith('/'):
                        img_data['src'] = urljoin(base_url, src)
                    else:
                        img_data['src'] = src
                    
                    # Combine alt and title for description
                    description_parts = []
                    if img_data['alt']:
                        description_parts.append(f"Alt: {img_data['alt']}")
                    if img_data['title']:
                        description_parts.append(f"Title: {img_data['title']}")
                    
                    img_data['description'] = '; '.join(description_parts)
                    images.append(img_data)
            
            return images
            
        except Exception as e:
            st.warning(f"Image extraction failed: {str(e)}")
            return []
    
    def _extract_visual_elements(self, html_content: str) -> List[Dict]:
        """Extract visual elements and their context"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            visual_elements = []
            
            # Extract videos
            videos = soup.find_all(['video', 'iframe'])
            for video in videos[:5]:  # Limit to first 5 videos
                element_data = {
                    'type': 'video',
                    'src': video.get('src', ''),
                    'title': video.get('title', ''),
                    'description': f"Video element: {video.get('title', 'No title')}"
                }
                visual_elements.append(element_data)
            
            # Extract embeds (social media, etc.)
            embeds = soup.find_all(['embed', 'object'])
            for embed in embeds[:3]:
                element_data = {
                    'type': 'embed',
                    'src': embed.get('src', ''),
                    'description': f"Embedded content: {embed.get('type', 'Unknown type')}"
                }
                visual_elements.append(element_data)
            
            return visual_elements
            
        except Exception as e:
            st.warning(f"Visual elements extraction failed: {str(e)}")
            return []
    
    def _capture_screenshot_selenium(self, url: str) -> Optional[str]:
        """Capture screenshot using Selenium"""
        try:
            if not SELENIUM_AVAILABLE:
                return None
            
            driver = webdriver.Chrome(
                options=self.chrome_options,
                service=webdriver.chrome.service.Service(ChromeDriverManager().install())
            )
            
            try:
                driver.get(url)
                driver.implicitly_wait(5)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Capture screenshot
                screenshot = driver.get_screenshot_as_png()
                
                # Convert to base64 for storage
                screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
                
                return screenshot_b64
                
            finally:
                driver.quit()
                
        except Exception as e:
            st.warning(f"Selenium screenshot failed: {str(e)}")
            return None
    
    def _capture_screenshot_playwright(self, url: str) -> Optional[str]:
        """Capture screenshot using Playwright with enhanced JavaScript support"""
        try:
            if not PLAYWRIGHT_AVAILABLE:
                return None
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set user agent to appear more like a real browser
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                try:
                    page.goto(url, timeout=30000)
                    
                    # Wait for content to load, especially for JavaScript-heavy sites
                    try:
                        page.wait_for_load_state('networkidle', timeout=15000)
                    except:
                        # If networkidle fails, wait for DOM content
                        page.wait_for_load_state('domcontentloaded', timeout=10000)
                    
                    # Additional wait for dynamic content
                    page.wait_for_timeout(3000)
                    
                    screenshot = page.screenshot(full_page=True)
                    screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
                    
                    return screenshot_b64
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            st.warning(f"Playwright screenshot failed: {str(e)}")
            return None
    
    def _capture_screenshot_fallback(self, url: str) -> Optional[str]:
        """Fallback screenshot method using requests"""
        try:
            # This is a simplified fallback - in practice, you might use a service
            # like htmlcsstoimage.com or similar
            return None
        except Exception as e:
            st.warning(f"Fallback screenshot failed: {str(e)}")
            return None
    
    def _extract_metadata(self, html_content: str, url: str) -> Dict:
        """Extract page metadata"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            metadata = {
                'title': '',
                'description': '',
                'author': '',
                'keywords': '',
                'og_title': '',
                'og_description': '',
                'og_image': '',
                'twitter_title': '',
                'twitter_description': '',
                'twitter_image': ''
            }
            
            # Basic meta tags
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()
            
            # Meta description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag:
                metadata['description'] = desc_tag.get('content', '')
            
            # Author
            author_tag = soup.find('meta', attrs={'name': 'author'})
            if author_tag:
                metadata['author'] = author_tag.get('content', '')
            
            # Keywords
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_tag:
                metadata['keywords'] = keywords_tag.get('content', '')
            
            # Open Graph tags
            og_title = soup.find('meta', property='og:title')
            if og_title:
                metadata['og_title'] = og_title.get('content', '')
            
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                metadata['og_description'] = og_desc.get('content', '')
            
            og_image = soup.find('meta', property='og:image')
            if og_image:
                metadata['og_image'] = og_image.get('content', '')
            
            # Twitter tags
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title:
                metadata['twitter_title'] = twitter_title.get('content', '')
            
            twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
            if twitter_desc:
                metadata['twitter_description'] = twitter_desc.get('content', '')
            
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image:
                metadata['twitter_image'] = twitter_image.get('content', '')
            
            return metadata
            
        except Exception as e:
            st.warning(f"Metadata extraction failed: {str(e)}")
            return {}
    
    def get_visual_content_summary(self, analysis_result: Dict) -> str:
        """Generate a summary of visual content for analysis"""
        summary_parts = []
        
        # Add text content
        if analysis_result.get('text_content'):
            summary_parts.append(f"Text Content: {analysis_result['text_content'][:500]}...")
        
        # Add image descriptions
        images = analysis_result.get('images', [])
        if images:
            summary_parts.append("Images found:")
            for img in images[:5]:  # Limit to first 5 images
                if img.get('description'):
                    summary_parts.append(f"- {img['description']}")
        
        # Add visual elements
        visual_elements = analysis_result.get('visual_elements', [])
        if visual_elements:
            summary_parts.append("Visual elements:")
            for element in visual_elements:
                summary_parts.append(f"- {element.get('description', 'Unknown element')}")
        
        # Add metadata
        metadata = analysis_result.get('metadata', {})
        if metadata.get('title'):
            summary_parts.append(f"Page Title: {metadata['title']}")
        if metadata.get('description'):
            summary_parts.append(f"Description: {metadata['description']}")
        
        return "\n".join(summary_parts)
    
    def is_visual_analysis_available(self) -> bool:
        """Check if visual analysis tools are available"""
        return SELENIUM_AVAILABLE or PLAYWRIGHT_AVAILABLE
