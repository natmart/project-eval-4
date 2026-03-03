"""
Main API facade for the pyshort URL shortener
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pyshort.storage import InMemoryStorage
from pyshort.stats import StatsTracker
from pyshort.generator import generate_random_code, generate_custom_code
from pyshort.validator import validate_url as validate_url_full, normalize_url
from pyshort.models import ShortURL


class URLShortener:
    """
    Main facade class for the URL shortener application.
    
    This class integrates all components (generator, validator, storage, stats)
    into a simple, easy-to-use API.
    """
    
    def __init__(self, storage=None, stats_tracker=None):
        """
        Initialize the URLShortener.
        
        Args:
            storage: Optional storage backend. Uses InMemoryStorage if not provided.
            stats_tracker: Optional stats tracker. Uses StatsTracker if not provided.
        """
        self._storage = storage or InMemoryStorage()
        self._stats = stats_tracker or StatsTracker()
    
    def shorten(
        self, 
        url: str, 
        custom_code: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> ShortURL:
        """
        Create a short URL for the given URL.
        
        Args:
            url: The original URL to shorten
            custom_code: Optional custom short code. If not provided, a random code is generated.
            expires_in_days: Optional number of days before the URL expires
            
        Returns:
            The ShortURL object that was created
            
        Raises:
            ValueError: If the URL is invalid or the custom code is already taken
        """
        # Validate the URL
        if not validate_url_full(url):
            raise ValueError(f"Invalid URL: {url}")
        
        # Normalize the URL
        normalized_url = normalize_url(url)
        
        # Generate or validate the short code
        if custom_code:
            if custom_code.strip() == "":
                raise ValueError("Custom code cannot be empty")
            
            # Validate custom code format
            code = generate_custom_code(custom_code)
            if not code:
                raise ValueError(f"Invalid custom code format: {custom_code}")
            
            short_code = code
        else:
            # Generate a random code
            short_code = generate_random_code()
        
        # Check if the code is already taken
        if self._storage.exists(short_code):
            if custom_code:
                raise ValueError(f"Short code '{custom_code}' is already taken")
            else:
                # If random code is taken, try again (up to 10 times)
                for _ in range(10):
                    short_code = generate_random_code()
                    if not self._storage.exists(short_code):
                        break
                else:
                    raise RuntimeError("Could not generate a unique short code")
        
        # Calculate expiration date
        expires_at = None
        if expires_in_days is not None and expires_in_days > 0:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        # Create the ShortURL object
        short_url = ShortURL(
            original_url=normalized_url,
            short_code=short_code,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        # Save to storage
        if not self._storage.save(short_url):
            raise RuntimeError(f"Failed to save URL with code: {short_code}")
        
        # Record stats
        self._stats.record_url_created(short_code)
        
        return short_url
    
    def resolve(self, short_code: str, track_click: bool = True) -> Optional[str]:
        """
        Resolve a short code to the original URL.
        
        Args:
            short_code: The short code to resolve
            track_click: Whether to record this as a click (default: True)
            
        Returns:
            The original URL if found and not expired, None otherwise
        """
        short_url = self._storage.get(short_code)
        
        if not short_url:
            return None
        
        # Check expiration
        if short_url.is_expired:
            return None
        
        # Track the click
        if track_click:
            self._stats.record_click(short_code)
            short_url.increment_clicks()
        
        return short_url.original_url
    
    def get_stats(self, short_code: Optional[str] = None) -> Dict:
        """
        Get statistics for a specific URL or overall statistics.
        
        Args:
            short_code: Optional short code to get URL-specific stats.
                       If None, returns overall statistics.
        
        Returns:
            Dictionary containing statistics
        """
        return self._stats.get_stats(short_code)
    
    def delete(self, short_code: str) -> bool:
        """
        Delete a short URL.
        
        Args:
            short_code: The short code to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        return self._storage.delete(short_code)
    
    def exists(self, short_code: str) -> bool:
        """
        Check if a short code exists and is valid (not expired).
        
        Args:
            short_code: The short code to check
            
        Returns:
            True if the short code exists and is valid, False otherwise
        """
        short_url = self._storage.get(short_code)
        if not short_url:
            return False
        
        # Check if expired
        if short_url.is_expired:
            return False
        
        return True
    
    def get_all_urls(self) -> List[ShortURL]:
        """
        Get all stored URLs.
        
        Returns:
            List of all ShortURL objects
        """
        return self._storage.get_all()
    
    def get_daily_stats(self) -> Dict[str, int]:
        """
        Get click statistics grouped by day.
        
        Returns:
            Dictionary mapping dates to click counts
        """
        return self._stats.get_daily_stats()
    
    def get_top_urls(self, limit: int = 5) -> List[Dict]:
        """
        Get the top URLs by click count.
        
        Args:
            limit: Maximum number of URLs to return
        Returns:
            List of dictionaries with short_code and click_count
        """
        return self._stats.get_top_urls(limit)
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired URLs from storage.
        
        Returns:
            Number of URLs that were cleaned up
        """
        all_urls = self._storage.get_all()
        count = 0
        
        for url in all_urls:
            if url.is_expired:
                if self._storage.delete(url.short_code):
                    count += 1
        
        return count