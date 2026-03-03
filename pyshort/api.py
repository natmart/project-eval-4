"""
Main URL shortener API that integrates all components
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Set, List
from pyshort.models import ShortURL
from pyshort.generator import generate_random_code, generate_custom_code
from pyshort.validator import is_url_safe, normalize_url, DEFAULT_BLOCKED_DOMAINS
from pyshort.storage import InMemoryStorage
from pyshort.stats import StatsTracker


class URLShortener:
    """
    Main facade class for the URL shortener.
    
    This class coordinates between the generator, validator, storage, and stats modules
    to provide a complete URL shortening API.
    
    Example:
        >>> shortener = URLShortener()
        >>> short_code = shortener.shorten("https://example.com/long-url")
        >>> original = shortener.resolve(short_code)
        >>> stats = shortener.get_stats(short_code)
    """
    
    def __init__(
        self,
        blocked_domains: Optional[Set[str]] = None,
        default_code_length: int = 6,
        default_ttl_days: Optional[int] = None
    ):
        """
        Initialize a new URLShortener instance.
        
        Args:
            blocked_domains: Set of domains to block (default: DEFAULT_BLOCKED_DOMAINS)
            default_code_length: Default length for randomly generated codes (default: 6)
            default_ttl_days: Default time-to-live in days for URLs (default: None = no expiration)
        """
        self.storage = InMemoryStorage()
        self.stats = StatsTracker()
        self.blocked_domains = blocked_domains or DEFAULT_BLOCKED_DOMAINS.copy()
        self.default_code_length = default_code_length
        self.default_ttl_days = default_ttl_days
    
    def shorten(
        self,
        url: str,
        custom_code: Optional[str] = None,
        code_length: Optional[int] = None,
        expires_at: Optional[datetime] = None,
        ttl_days: Optional[int] = None
    ) -> str:
        """
        Create a short URL for the given original URL.
        
        This method:
        1. Validates and normalizes the URL
        2. Checks that the domain is not blocked
        3. Generates or validates a custom short code
        4. Stores the URL and records statistics
        
        Args:
            url: The original URL to shorten
            custom_code: Optional custom short code (if None, generates random code)
            code_length: Length for random code (if custom_code is None)
            expires_at: Optional expiration datetime (overrides ttl_days)
            ttl_days: Optional time-to-live in days (overrides default_ttl_days)
            
        Returns:
            The short code for the shortened URL
            
        Raises:
            ValueError: If the URL is invalid, blocked, or code already exists
        """
        # Validate URL safety
        is_safe, error_msg = is_url_safe(url, blocked_domains=self.blocked_domains)
        if not is_safe:
            raise ValueError(f"Cannot shorten URL: {error_msg}")
        
        # Normalize the URL
        normalized_url = normalize_url(url)
        if not normalized_url:
            raise ValueError(f"Cannot normalize URL: {url}")
        
        # Determine expiration
        if expires_at is None:
            if ttl_days is not None:
                expires_at = datetime.now() + timedelta(days=ttl_days)
            elif self.default_ttl_days is not None:
                expires_at = datetime.now() + timedelta(days=self.default_ttl_days)
        
        # Generate or validate short code
        if custom_code:
            short_code = generate_custom_code(custom_code)
        else:
            length = code_length or self.default_code_length
            # Generate a unique code
            max_attempts = 10
            for _ in range(max_attempts):
                short_code = generate_random_code(length)
                if not self.storage.exists(short_code):
                    break
            else:
                raise ValueError("Failed to generate unique short code after multiple attempts")
        
        # Check if code already exists
        if self.storage.exists(short_code):
            raise ValueError(f"Short code '{short_code}' already exists")
        
        # Create ShortURL object
        short_url = ShortURL(
            original_url=normalized_url,
            short_code=short_code,
            created_at=datetime.now(),
            click_count=0,
            expires_at=expires_at
        )
        
        # Save to storage
        self.storage.save(short_url)
        
        # Record statistics
        self.stats.record_url_created(short_code, short_url.created_at)
        
        return short_code
    
    def resolve(self, short_code: str) -> Optional[str]:
        """
        Retrieve and return the original URL for a given short code.
        
        This method:
        1. Looks up the short code in storage
        2. Checks if the URL has expired
        3. Records a click for statistics
        4. Returns the original URL
        
        Args:
            short_code: The short code to resolve
            
        Returns:
            The original URL, or None if not found or expired
        """
        short_url = self.storage.get(short_code)
        
        if short_url is None:
            return None
        
        # Check expiration
        if short_url.is_expired:
            return None
        
        # Record click
        short_url.increment_clicks()
        self.stats.record_click(short_code)
        
        # Update in storage
        self.storage.save(short_url)
        
        return short_url.original_url
    
    def get_stats(self, short_code: Optional[str] = None) -> Dict:
        """
        Get statistics for the URL shortener.
        
        Args:
            short_code: Optional short code to get stats for a specific URL
            
        Returns:
            If short_code is provided: Stats for that specific URL
            If short_code is None: Overall statistics for all URLs
        """
        if short_code:
            # Get stats for specific URL
            url_stats = self.stats.get_url_stats(short_code)
            
            # Add URL info from storage
            short_url = self.storage.get(short_code)
            if short_url:
                url_stats.update({
                    'original_url': short_url.original_url,
                    'created_at': short_url.created_at.isoformat(),
                    'expires_at': short_url.expires_at.isoformat() if short_url.expires_at else None,
                    'is_expired': short_url.is_expired,
                })
            
            return url_stats
        else:
            # Get overall stats
            overall_stats = self.stats.get_stats()
            overall_stats['total_urls_in_storage'] = self.storage.count()
            return overall_stats
    
    def delete(self, short_code: str) -> bool:
        """
        Delete a short URL.
        
        Args:
            short_code: The short code to delete
            
        Returns:
            True if the URL was deleted, False if it didn't exist
        """
        return self.storage.delete(short_code)
    
    def exists(self, short_code: str) -> bool:
        """
        Check if a short code exists.
        
        Args:
            short_code: The short code to check
            
        Returns:
            True if the short code exists, False otherwise
        """
        return self.storage.exists(short_code)
    
    def get_all_urls(self) -> List[Dict]:
        """
        Get all shortened URLs with their stats.
        
        Returns:
            List of dictionaries containing URL information and stats
        """
        urls = []
        for short_code, short_url in self.storage.get_all().items():
            stats = self.stats.get_url_stats(short_code)
            urls.append({
                'short_code': short_code,
                'original_url': short_url.original_url,
                'created_at': short_url.created_at.isoformat(),
                'click_count': short_url.click_count,
                'expires_at': short_url.expires_at.isoformat() if short_url.expires_at else None,
                'is_expired': short_url.is_expired,
                'tracked_clicks': stats.get('clicks', 0),
            })
        return urls
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """
        Get daily statistics for the last N days.
        
        Args:
            days: Number of days to include (default: 7)
            
        Returns:
            List of daily statistics, most recent first
        """
        return self.stats.get_daily_stats(days)
    
    def get_top_urls(self, limit: int = 10) -> List[Dict]:
        """
        Get the most-clicked URLs.
        
        Args:
            limit: Maximum number of URLs to return (default: 10)
            
        Returns:
            List of URLs with click counts, sorted by clicks (highest first)
        """
        return self.stats.get_top_urls(limit)
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired URLs from storage.
        
        Returns:
            Number of URLs removed
        """
        removed = 0
        all_urls = self.storage.get_all()
        
        for short_code, short_url in list(all_urls.items()):
            if short_url.is_expired:
                if self.storage.delete(short_code):
                    removed += 1
        
        return removed