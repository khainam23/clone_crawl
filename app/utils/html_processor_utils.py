"""
HTML processing utilities for Mitsui crawling
"""
import re
from typing import Optional, Dict
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
    
    @classmethod
    def extract_dt_dd_content(cls, html: str, dt_label: str) -> Optional[str]:
        """
        Extract content from <dt>label</dt><dd>content</dd> pattern
        
        Args:
            html: HTML string to search in
            dt_label: Label text to find in <dt> tag
            
        Returns:
            Cleaned content from <dd> tag or None if not found
        """
        pattern = rf'<dt[^>]*>{dt_label}</dt>\s*<dd[^>]*>(.*?)</dd>'
        content = cls.find(pattern, html)
        return cls.clean_html(content) if content else None
    
    @classmethod
    def find_dt_dd(cls, html: str, dt_label: str) -> Optional[str]:
        """
        Find and clean content from <dt>label</dt><dd>content</dd> pattern
        Alternative method with different pattern matching
        
        Args:
            html: HTML string to search in
            dt_label: Label text to find in <dt> tag
            
        Returns:
            Cleaned content from <dd> tag or None if not found
        """
        content = cls.find(rf'{dt_label}.*?<dd[^>]*>(.*?)</dd>', html)
        return cls.clean_html(content).strip() if content else None
    
    @classmethod
    def find_td(cls, html: str, th_label: str) -> Optional[str]:
        """
        Find and clean content from table <th>label</th>...<td>content</td> pattern
        
        Args:
            html: HTML string to search in
            th_label: Label text to find in <th> tag
            
        Returns:
            Cleaned content from <td> tag or None if not found
        """
        content = cls.find(rf'{th_label}.*?<td[^>]*>(.*?)</td>', html)
        return cls.clean_html(content).strip() if content else None
    
    @classmethod
    def parse_all_dt_dd(cls, html: str) -> Dict[str, str]:
        """
        Parse ALL <dt>label</dt><dd>content</dd> pairs in one pass
        
        Args:
            html: HTML string to parse
            
        Returns:
            Dictionary mapping dt labels to cleaned dd content
        """
        result = {}
        pattern = cls.compile_regex(r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>')
        
        for match in pattern.finditer(html):
            label = cls.clean_html(match.group(1)).strip()
            content = match.group(2).strip()  # Keep raw HTML for now
            if label:
                result[label] = content
        
        return result
    
    @classmethod
    def parse_all_th_td(cls, html: str) -> Dict[str, str]:
        """
        Parse ALL <th>label</th>...<td>content</td> pairs in one pass
        
        Args:
            html: HTML string to parse
            
        Returns:
            Dictionary mapping th labels to raw td content (not cleaned)
        """
        result = {}
        # Match th label followed by td content (may have other tags in between)
        pattern = cls.compile_regex(r'<th[^>]*>(.*?)</th>.*?<td[^>]*>(.*?)</td>')
        
        for match in pattern.finditer(html):
            label = cls.clean_html(match.group(1)).strip()
            content = match.group(2).strip()  # Keep raw HTML
            if label:
                result[label] = content
        
        return result
    
htmlProcessor = HtmlProcessor()