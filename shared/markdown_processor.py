#!/usr/bin/env python3
"""
Shared Markdown Processor with Confluence-style Extensions
Used by both blog and documents systems

This module provides a unified markdown processing system that can be used
by both the blog system and the documents system.
"""
import sys
from pathlib import Path

# Import config to get BLOG_RESOURCES path
try:
    from admin.config import BLOG_RESOURCES
    BLOG_DIR = BLOG_RESOURCES
except ImportError:
    # Fallback to old path if config not available
    BLOG_DIR = Path(__file__).resolve().parents[1] / "admin" / "resources" / "blog"

sys.path.insert(0, str(BLOG_DIR))

# Import BlogManager - note: file is blog-manager.py but module name uses underscore
import importlib.util
blog_manager_path = BLOG_DIR / "blog-manager.py"
if not blog_manager_path.exists():
    raise FileNotFoundError(f"BlogManager not found at {blog_manager_path}")

spec = importlib.util.spec_from_file_location("blog_manager", blog_manager_path)
blog_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blog_manager_module)
BlogManager = blog_manager_module.BlogManager


class SharedMarkdownProcessor:
    """
    Wrapper around BlogManager's markdown processing functionality.
    This allows both blog and documents systems to use the same markdown processor.
    """
    
    def __init__(self):
        # Create a BlogManager instance just for markdown processing
        # Pass the correct blog root path from config
        try:
            from admin.config import BLOG_RESOURCES
            blog_root = str(BLOG_RESOURCES)
        except ImportError:
            # Fallback to old path if config not available
            blog_root = str(Path(__file__).resolve().parents[1] / "admin" / "resources" / "blog")
        
        self._processor = BlogManager(blog_root=blog_root)
        # Reset tab counter for each document
        self._processor._tab_counter = 0
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """
        Convert markdown text to HTML with all Confluence-style extensions.
        
        Args:
            markdown_text: Raw markdown content
            
        Returns:
            HTML string with all custom components rendered
        """
        return self._processor.markdown_to_html(markdown_text)
    
    def process_markdown(self, markdown_text: str) -> str:
        """
        Alias for markdown_to_html for consistency.
        """
        return self.markdown_to_html(markdown_text)


# Convenience function for direct use
def process_markdown(markdown_text: str) -> str:
    """
    Process markdown text with all Confluence-style extensions.
    
    Usage:
        from shared.markdown_processor import process_markdown
        html = process_markdown("# Hello World")
    """
    processor = SharedMarkdownProcessor()
    return processor.markdown_to_html(markdown_text)
