"""
Data models for the pyshort URL shortener application.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate that a string is a properly formatted URL.
    
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
        # Check that we have both a scheme and netloc for a valid URL
        return all([result.scheme, result.netloc])
    except Exception:
        return False


@dataclass
class ShortURL:
    """
    Represents a shortened URL with its metadata.
    
    Attributes:
        original_url: The full, original URL that was shortened
        short_code: The unique short code that identifies this URL
        created_at: Timestamp when the URL was shortened
        click_count: Number of times the short URL has been accessed
        expires_at: Optional timestamp when the short URL will expire
        
    Examples:
        >>> short_url = ShortURL(
        ...     original_url="https://example.com/very/long/path",
        ...     short_code="abc12",
        ...     created_at=datetime.now(),
        ...     click_count=0
        ... )
        >>> short_url.original_url
        'https://example.com/very/long/path'
    """
    original_url: str
    short_code: str
    created_at: datetime
    click_count: int = 0
    expires_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """
        Validate the URL after initialization.
        
        Raises:
            ValueError: If the original_url is not a valid URL
        """
        if not validate_url(self.original_url):
            raise ValueError(f"Invalid URL: {self.original_url}")
        
        if not self.short_code:
            raise ValueError("short_code cannot be empty")
        
        if self.click_count < 0:
            raise ValueError("click_count cannot be negative")
    
    @property
    def is_expired(self) -> bool:
        """
        Check if the short URL has expired.
        
        Returns:
            True if the URL has expired (and expires_at is set),
            False otherwise
        """
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def increment_clicks(self) -> None:
        """Increment the click count by 1."""
        self.click_count += 1
    
    def __repr__(self) -> str:
        """String representation of the ShortURL."""
        expires = self.expires_at.isoformat() if self.expires_at else "None"
        return (
            f"ShortURL(original_url='{self.original_url}', "
            f"short_code='{self.short_code}', "
            f"click_count={self.click_count}, "
            f"expires_at={expires})"
        )