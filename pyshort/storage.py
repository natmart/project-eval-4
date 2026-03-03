"""
In-memory storage backend for the pyshort URL shortener
"""
from typing import Dict, List, Optional
from pyshort.models import ShortURL


class InMemoryStorage:
    """
    In-memory storage backend for storing ShortURL objects.
    
    This is a simple implementation that stores URLs in memory.
    For production use, you might want to implement a database-backed
    storage solution.
    """
    
    def __init__(self):
        """Initialize an empty storage."""
        self._urls: Dict[str, ShortURL] = {}
    
    def save(self, short_url: ShortURL) -> bool:
        """
        Save a ShortURL object to storage.
        
        Args:
            short_url: The ShortURL object to save
            
        Returns:
            True if saved successfully, False if a URL with this
            short_code already exists
        """
        if short_url.short_code in self._urls:
            return False
        self._urls[short_url.short_code] = short_url
        return True
    
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
            True if deleted successfully, False if not found
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
    
    def get_all(self) -> List[ShortURL]:
        """
        Get all stored ShortURL objects.
        
        Returns:
            List of all ShortURL objects
        """
        return list(self._urls.values())
    
    def clear(self) -> None:
        """Clear all stored URLs."""
        self._urls.clear()
    
    def count(self) -> int:
        """
        Get the total number of stored URLs.
        
        Returns:
            Number of stored URLs
        """
        return len(self._urls)