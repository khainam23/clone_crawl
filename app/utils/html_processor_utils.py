"""
HTML processing utilities for Mitsui crawling
"""
import re
from typing import Optional
from functools import lru_cache

class HtmlProcessor:
    """Handles HTML processing and text cleaning"""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def compile_regex(pattern: str, flags: int = re.DOTALL | re.IGNORECASE) -> re.Pattern:
        """Cache compiled regex patterns for better performance"""
        return re.compile(pattern, flags)
    
    @classmethod
    def find(cls, pattern: str, html: str) -> Optional[str]:
        """Find pattern in HTML with cached regex"""
        regex = cls.compile_regex(pattern)
        match = regex.search(html)
        return match.group(1).strip() if match else None
    
    @classmethod
    def clean_html(cls, text: str) -> str:
        """Remove HTML tags and clean text"""
        if not text:
            return ""
        # Use cached regex for HTML tag removal
        html_tag_regex = cls.compile_regex(r'<[^>]+>')
        cleaned = html_tag_regex.sub('', text).strip()
        # Clean HTML entities
        cleaned = cleaned.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return cleaned
    
    @classmethod
    def clean_html_before_processing(cls, html: str) -> str:
        """Clean HTML before processing with cached regex"""
        # Remove related sections
        related_pattern = cls.compile_regex(r'<section[^>]*class="[^"]*--related[^"]*"[^>]*>.*?</section>')
        html = related_pattern.sub('', html)
        
        # Remove Japanese related properties text
        japanese_pattern = cls.compile_regex(r'この部屋をチェックした人は、こんな部屋もチェックしています。.*?(?=<footer|$)')
        html = japanese_pattern.sub('', html)
        
        return html
    
htmlProcessor = HtmlProcessor()