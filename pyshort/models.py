"""
Data models for the pyshort URL shortener
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate a URL string.
    
    A valid URL must have both a scheme (e.g., http, https) and a network location.
    
    Args:
        url: The URL string to validate
        
    Returns:
        True if the URL is valid, False otherwise
        
    Examples:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("not-a-url")
        False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


@dataclass
class ShortURL:
    """
    Represents a shortened URL with all its metadata.
    
    Attributes:
        original_url: The original URL being shortened
        short_code: The unique short code that identifies this URL
        created_at: When the URL was shortened
        click_count: Number of times the short URL has been accessed (default: 0)
        expires_at: Optional expiration time for the URL (default: None)
        
    Raises:
        ValueError: If the URL is invalid or short_code is empty
    """
    original_url: str
    short_code: str
    created_at: datetime
    click_count: int = 0
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the ShortURL after initialization."""
        if not validate_url(self.original_url):
            raise ValueError(f"Invalid URL: {self.original_url}")
        if not self.short_code or not self.short_code.strip():
            raise ValueError("short_code cannot be empty")
        if self.click_count < 0:
            raise ValueError("click_count cannot be negative")
    
    @property
    def is_expired(self) -> bool:
        """
        Check if the URL has expired.
        
        Returns:
            True if the URL has expired (expires_at is in the past),
            False if it hasn't expired or has no expiration
        """
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def increment_clicks(self) -> int:
        """
        Increment the click count.
        
        Returns:
            The new click count
        """
        self.click_count += 1
        return self.click_count