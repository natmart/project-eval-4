"""
Data models for pyshort URL shortener
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate that a URL has both scheme and netloc.
    
    Args:
        url: The URL string to validate
        
    Returns:
        True if the URL is valid, False otherwise
        
    Examples:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("example.com")
        False
    """
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


@dataclass
class ShortURL:
    """
    Represents a shortened URL with metadata.
    
    Attributes:
        original_url: The full URL to be shortened
        short_code: Unique short code identifier
        created_at: Creation timestamp
        click_count: Number of times the short URL has been accessed
        expires_at: Optional expiration datetime
        
    Examples:
        >>> from datetime import datetime, timedelta
        >>> url = ShortURL(
        ...     original_url="https://example.com",
        ...     short_code="abc123",
        ...     created_at=datetime.now(),
        ...     expires_at=datetime.now() + timedelta(days=7)
        ... )
    """
    original_url: str
    short_code: str
    created_at: datetime = field(default_factory=datetime.now)
    click_count: int = 0
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the ShortURL data after initialization."""
        if not validate_url(self.original_url):
            raise ValueError(f"Invalid URL: {self.original_url}")
        if not self.short_code or not self.short_code.strip():
            raise ValueError("Short code cannot be empty")
        if self.click_count < 0:
            raise ValueError("Click count cannot be negative")
    
    @property
    def is_expired(self) -> bool:
        """
        Check if the URL has expired.
        
        Returns:
            True if the URL has expired, False otherwise
            
        Examples:
            >>> from datetime import datetime, timedelta
            >>> url = ShortURL(
            ...     original_url="https://example.com",
            ...     short_code="abc123",
            ...     expires_at=datetime.now() - timedelta(days=1)
            ... )
            >>> url.is_expired
            True
        """
        if self.expires_at is None:
            return False
        return datetime.now() >= self.expires_at
    
    def increment_clicks(self) -> int:
        """
        Increment the click counter.
        
        Returns:
            The new click count
            
        Examples:
            >>> url = ShortURL(
            ...     original_url="https://example.com",
            ...     short_code="abc123"
            ... )
            >>> url.increment_clicks()
            1
            >>> url.increment_clicks()
            2
        """
        self.click_count += 1
        return self.click_count