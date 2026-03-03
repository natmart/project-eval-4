"""
Storage backends for pyshort URL shortener
"""

from abc import ABC, abstractmethod
from threading import Lock
from typing import Dict, List, Optional
from pyshort.models import ShortURL


class BaseStorage(ABC):
    """
    Abstract base class defining the storage interface for URL shortener.
    
    All storage implementations must inherit from this class and implement
    all abstract methods.
    """
    
    @abstractmethod
    def save(self, short_url: ShortURL) -> None:
        """
        Save a ShortURL object to storage.
        
        Args:
            short_url: The ShortURL object to save
            
        Raises:
            ValueError: If a URL with the same short_code already exists
        """
        pass
    
    @abstractmethod
    def get_by_code(self, short_code: str) -> Optional[ShortURL]:
        """
        Retrieve a ShortURL by its short code.
        
        Args:
            short_code: The short code to look up
            
        Returns:
            The ShortURL if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_url(self, original_url: str) -> Optional[ShortURL]:
        """
        Retrieve a ShortURL by its original URL.
        
        Args:
            original_url: The original URL to look up
            
        Returns:
            The ShortURL if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, short_code: str) -> bool:
        """
        Delete a ShortURL by its short code.
        
        Args:
            short_code: The short code of the URL to delete
            
        Returns:
            True if the URL was deleted, False if it wasn't found
        """
        pass
    
    @abstractmethod
    def list_all(self) -> List[ShortURL]:
        """
        List all stored ShortURL objects.
        
        Returns:
            A list of all ShortURL objects in storage
        """
        pass


class InMemoryStorage(BaseStorage):
    """
    In-memory implementation of the storage backend.
    
    Uses Python dictionaries to store ShortURL objects. Thread-safe
    for basic operations using a threading.Lock.
    
    Note: This storage is not persistent - data is lost when the
    program exits. Use for testing or development only.
    
    Attributes:
        _urls_by_code: Dictionary mapping short codes to ShortURL objects
        _urls_by_url: Dictionary mapping original URLs to ShortURL objects
        _lock: Thread lock for thread-safe operations
    """
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self._urls_by_code: Dict[str, ShortURL] = {}
        self._urls_by_url: Dict[str, ShortURL] = {}
        self._lock: Lock = Lock()
    
    def save(self, short_url: ShortURL) -> None:
        """
        Save a ShortURL object to in-memory storage.
        
        Args:
            short_url: The ShortURL object to save
            
        Raises:
            ValueError: If a URL with the same short_code or original_url
                       already exists
        """
        with self._lock:
            # Check for duplicate short code
            if short_url.short_code in self._urls_by_code:
                raise ValueError(
                    f"ShortURL with code '{short_url.short_code}' already exists"
                )
            
            # Check for duplicate original URL
            if short_url.original_url in self._urls_by_url:
                raise ValueError(
                    f"ShortURL with original URL '{short_url.original_url}' already exists"
                )
            
            # Save to both indexes
            self._urls_by_code[short_url.short_code] = short_url
            self._urls_by_url[short_url.original_url] = short_url
    
    def get_by_code(self, short_code: str) -> Optional[ShortURL]:
        """
        Retrieve a ShortURL by its short code.
        
        Args:
            short_code: The short code to look up
            
        Returns:
            The ShortURL if found, None otherwise
        """
        with self._lock:
            return self._urls_by_code.get(short_code)
    
    def get_by_url(self, original_url: str) -> Optional[ShortURL]:
        """
        Retrieve a ShortURL by its original URL.
        
        Args:
            original_url: The original URL to look up
            
        Returns:
            The ShortURL if found, None otherwise
        """
        with self._lock:
            return self._urls_by_url.get(original_url)
    
    def delete(self, short_code: str) -> bool:
        """
        Delete a ShortURL by its short code.
        
        Args:
            short_code: The short code of the URL to delete
            
        Returns:
            True if the URL was deleted, False if it wasn't found
        """
        with self._lock:
            short_url = self._urls_by_code.get(short_code)
            if short_url is None:
                return False
            
            # Remove from both indexes
            del self._urls_by_code[short_code]
            del self._urls_by_url[short_url.original_url]
            return True
    
    def list_all(self) -> List[ShortURL]:
        """
        List all stored ShortURL objects.
        
        Returns:
            A list of all ShortURL objects in storage
        """
        with self._lock:
            return list(self._urls_by_code.values())
    
    def clear(self) -> None:
        """
        Clear all stored ShortURL objects.
        
        Useful for testing and development.
        """
        with self._lock:
            self._urls_by_code.clear()
            self._urls_by_url.clear()
    
    def count(self) -> int:
        """
        Get the number of stored ShortURL objects.
        
        Returns:
            The count of stored URLs
        """
        with self._lock:
            return len(self._urls_by_code)