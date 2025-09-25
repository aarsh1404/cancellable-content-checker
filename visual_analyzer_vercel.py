"""
Lightweight visual content analyzer for Vercel deployment
Does not include Playwright/Selenium to stay under size limits
"""

import os
import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin
import streamlit as st

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

class VisualURLAnalyzerVercel:
    """Lightweight URL analyzer for Vercel deployment (no browser automation)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_url_enhanced(self, url: str) -> Dict:
        """
        Enhanced URL analysis without browser automation (Vercel-compatible)
        
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
            
            # Get basic page content
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                result['text_content'] = self._extract_text_from_html(response.text, url)
            except Exception as e:
                result['error'] = f"Failed to fetch basic content: {str(e)}"
                return result
            
            # Extract images and visual elements
            try:
                result['images'] = self._extract_images(response.text, url)
                result['visual_elements'] = self._extract_visual_elements(response.text)
            except Exception as e:
                st.warning(f"Visual extraction warning: {str(e)}")
            
            # Extract metadata
            result['metadata'] = self._extract_metadata(response.text, url)
            
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
            if not BS4_AVAILABLE:
                raise Exception("BeautifulSoup not available")
            
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
            if not BS4_AVAILABLE:
                return []
            
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
            if not BS4_AVAILABLE:
                return []
            
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
    
    def _extract_metadata(self, html_content: str, url: str) -> Dict:
        """Extract page metadata"""
        try:
            if not BS4_AVAILABLE:
                return {}
            
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
        return BS4_AVAILABLE
