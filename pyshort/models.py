"""
Data models for the URL shortener application.

This module provides URL validation and the ShortURL dataclass for storing
URL information.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate a URL string.
    
    A valid URL must have both a scheme (e.g., http, https) and a netloc (domain).
    
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
        parsed = urlparse(url)
        # Valid URLs must have both scheme and netloc
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


class InvalidURLError(ValueError):
    """Raised when an invalid URL is provided."""
    pass


@dataclass
class ShortURL:
    """
    Represents a shortened URL with metadata.
    
    Attributes:
        original_url: The full original URL to be shortened
        short_code: Unique short code identifier for the URL
        created_at: Timestamp when the URL was created
        click_count: Number of times the shortened URL has been accessed
        expires_at: Optional expiration timestamp after which URL is invalid
        
    Examples:
        >>> from datetime import datetime, timedelta
        >>> url = ShortURL(
        ...     original_url="https://example.com/very/long/path",
        ...     short_code="abc123",
        ...     created_at=datetime.now()
        ... )
        >>> url.increment_clicks()
        >>> url.click_count
        1
    """
    original_url: str
    short_code: str
    created_at: datetime
    click_count: int = field(default=0)
    expires_at: Optional[datetime] = field(default=None)
    
    def __post_init__(self):
        """Validate the ShortURL fields after initialization."""
        if not validate_url(self.original_url):
            raise InvalidURLError(f"Invalid URL: {self.original_url}")
        if not self.short_code:
            raise ValueError("short_code cannot be empty")
        if self.click_count < 0:
            raise ValueError("click_count cannot be negative")
    
    @property
    def is_expired(self) -> bool:
        """
        Check if the URL has expired.
        
        Returns:
            True if expires_at is set and the current time is past expires_at,
            False otherwise
        """
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def increment_clicks(self) -> None:
        """Increment the click count by 1."""
        self.click_count += 1