"""
In-memory storage backend for the pyshort URL shortener
"""
from datetime import datetime
from typing import Dict, Optional
from pyshort.models import ShortURL


class InMemoryStorage:
    """
    Simple in-memory storage for ShortURL objects.
    
    This implementation stores URLs in a dictionary in memory.
    All data is lost when the application restarts.
    """
    
    def __init__(self):
        """Initialize an empty storage backend."""
        self._urls: Dict[str, ShortURL] = {}
    
    def save(self, url: ShortURL) -> ShortURL:
        """
        Save a ShortURL to storage.
        
        Args:
            url: The ShortURL object to save
            
        Returns:
            The saved ShortURL object
            
        Raises:
            ValueError: If a URL with the same short_code already exists
        """
        if url.short_code in self._urls:
            raise ValueError(f"Short code '{url.short_code}' already exists")
        
        self._urls[url.short_code] = url
        return url
    
    def get(self, short_code: str) -> Optional[ShortURL]:
        """
        Retrieve a ShortURL by its short code.
        
        Args:
            short_code: The short code to look up
            
        Returns:
            The ShortURL if found, None otherwise
        """
        return self._urls.get(short_code)
    
    def delete(self, short_code: str) -> bool:
        """
        Delete a ShortURL by its short code.
        
        Args:
            short_code: The short code to delete
            
        Returns:
            True if the URL was deleted, False if it didn't exist
        """
        if short_code in self._urls:
            del self._urls[short_code]
            return True
        return False
    
    def exists(self, short_code: str) -> bool:
        """
        Check if a short code exists in storage.
        
        Args:
            short_code: The short code to check
            
        Returns:
            True if the short code exists, False otherwise
        """
        return short_code in self._urls
    
    def get_all(self) -> Dict[str, ShortURL]:
        """
        Get all stored URLs.
        
        Returns:
            Dictionary mapping short codes to ShortURL objects
        """
        return self._urls.copy()
    
    def clear(self) -> None:
        """Clear all stored URLs."""
        self._urls.clear()
    
    def count(self) -> int:
        """
        Get the number of stored URLs.
        
        Returns:
            Number of URLs in storage
        """
        return len(self._urls)