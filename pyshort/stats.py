"""
Statistics tracker for URL shortener with thread-safe counters.

This module provides functionality to track clicks for URLs, aggregate daily statistics,
and retrieve top URLs by click count. All operations are thread-safe using threading.Lock.
"""

import threading
from collections import defaultdict
from datetime import date, datetime
from typing import Dict, List, Tuple


class StatsTracker:
    """
    Thread-safe statistics tracker for URL clicks.
    
    Tracks total clicks per URL short code, daily breakdown of clicks,
    and provides methods to retrieve top URLs. All mutations are protected
    by a threading.Lock ensuring thread-safe atomic operations.
    
    Attributes:
        _clicks: Dictionary mapping short codes to total click counts
        _daily_clicks: Nested dictionary mapping dates to short codes to click counts
        _lock: Threading lock for thread-safe operations
    
    Example:
        >>> tracker = StatsTracker()
        >>> tracker.track_click("abc123")
        >>> tracker.track_click("abc123")
        >>> tracker.track_click("xyz789")
        >>> tracker.get_click_count("abc123")
        2
        >>> tracker.get_top_urls(limit=2)
        [('abc123', 2), ('xyz789', 1)]
    """
    
    def __init__(self) -> None:
        """Initialize an empty StatsTracker with thread-safe counters."""
        self._clicks: Dict[str, int] = defaultdict(int)
        self._daily_clicks: Dict[date, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._lock = threading.Lock()
    
    def track_click(self, short_code: str, click_date: date = None) -> None:
        """
        Track a click for a URL short code with thread-safe atomic operation.
        
        Increments both the total click count for the short code and the
        daily click count for the specified date. If no date is provided,
        uses the current date.
        
        Args:
            short_code: The short code identifier for the URL
            click_date: Optional date for the click. Defaults to today.
            
        Raises:
            ValueError: If short_code is empty
            
        Example:
            >>> tracker = StatsTracker()
            >>> tracker.track_click("abc123")
            >>> tracker.track_click("abc123", date(2024, 1, 15))
        """
        if not short_code or not isinstance(short_code, str):
            raise ValueError("short_code must be a non-empty string")
        
        if click_date is None:
            click_date = date.today()
        
        # Atomic operation: acquire lock, update both counters, release lock
        with self._lock:
            self._clicks[short_code] += 1
            self._daily_clicks[click_date][short_code] += 1
    
    def get_click_count(self, short_code: str) -> int:
        """
        Get the total click count for a specific short code.
        
        Args:
            short_code: The short code identifier for the URL
            
        Returns:
            Total number of clicks for the short code, or 0 if not found
            
        Example:
            >>> tracker = StatsTracker()
            >>> tracker.track_click("abc123")
            >>> tracker.track_click("abc123")
            >>> tracker.get_click_count("abc123")
            2
        """
        with self._lock:
            return self._clicks.get(short_code, 0)
    
    def get_daily_stats(self, start_date: date = None, end_date: date = None) -> Dict[date, Dict[str, int]]:
        """
        Get daily statistics breakdown within an optional date range.
        
        Returns a dictionary mapping dates to dictionaries of short codes
        and their click counts for that date. If no date range is specified,
        returns all available daily statistics.
        
        Args:
            start_date: Optional start date (inclusive). Defaults to earliest date.
            end_date: Optional end date (inclusive). Defaults to latest date.
            
        Returns:
            Dictionary mapping dates to {short_code: click_count} dictionaries
            
        Example:
            >>> tracker = StatsTracker()
            >>> tracker.track_click("abc123", date(2024, 1, 15))
            >>> tracker.track_click("xyz789", date(2024, 1, 15))
            >>> stats = tracker.get_daily_stats()
            >>> stats[date(2024, 1, 15)]["abc123"]
            1
        """
        with self._lock:
            if start_date is None and end_date is None:
                # Return a copy to prevent external modification
                return {d: dict(clicks) for d, clicks in self._daily_clicks.items()}
            
            if start_date is None:
                # Filter by end date only
                return {
                    d: dict(clicks)
                    for d, clicks in self._daily_clicks.items()
                    if d <= end_date
                }
            
            if end_date is None:
                # Filter by start date only
                return {
                    d: dict(clicks)
                    for d, clicks in self._daily_clicks.items()
                    if d >= start_date
                }
            
            # Filter by date range
            return {
                d: dict(clicks)
                for d, clicks in self._daily_clicks.items()
                if start_date <= d <= end_date
            }
    
    def get_top_urls(self, limit: int = 10, min_clicks: int = 1) -> List[Tuple[str, int]]:
        """
        Get top URLs sorted by click count in descending order.
        
        Returns a list of tuples containing (short_code, click_count) sorted
        by click count in descending order. Only URLs with at least min_clicks
        are included.
        
        Args:
            limit: Maximum number of URLs to return. Use 0 for unlimited.
            min_clicks: Minimum number of clicks required to be included.
            
        Returns:
            List of (short_code, click_count) tuples, sorted by click count descending
            
        Example:
            >>> tracker = StatsTracker()
            >>> tracker.track_click("abc123")
            >>> tracker.track_click("abc123")
            >>> tracker.track_click("xyz789")
            >>> tracker.get_top_urls(limit=5)
            [('abc123', 2), ('xyz789', 1)]
        """
        with self._lock:
            # Filter by minimum clicks and sort by count descending
            sorted_urls = sorted(
                [(code, count) for code, count in self._clicks.items() if count >= min_clicks],
                key=lambda x: x[1],
                reverse=True
            )
            
            if limit > 0:
                return sorted_urls[:limit]
            return sorted_urls
    
    def get_total_clicks(self) -> int:
        """
        Get the total number of clicks across all URLs.
        
        Returns:
            Total click count across all short codes
            
        Example:
            >>> tracker = StatsTracker()
            >>> tracker.track_click("abc123")
            >>> tracker.track_click("xyz789")
            >>> tracker.get_total_clicks()
            2
        """
        with self._lock:
            return sum(self._clicks.values())
    
    def get_unique_urls(self) -> int:
        """
        Get the number of unique URLs (short codes) tracked.
        
        Returns:
            Number of unique short codes with at least one click
            
        Example:
            >>> tracker = StatsTracker()
            >>> tracker.track_click("abc123")
            >>> tracker.track_click("xyz789")
            >>> tracker.get_unique_urls()
            2
        """
        with self._lock:
            return len(self._clicks)
    
    def get_clicks_for_date(self, click_date: date) -> int:
        """
        Get total clicks for a specific date across all URLs.
        
        Args:
            click_date: The date to query
            
        Returns:
            Total number of clicks for the specified date
            
        Example:
            >>> tracker = StatsTracker()
            >>> tracker.track_click("abc123", date(2024, 1, 15))
            >>> tracker.track_click("xyz789", date(2024, 1, 15))
            >>> tracker.get_clicks_for_date(date(2024, 1, 15))
            2
        """
        with self._lock:
            return sum(self._daily_clicks.get(click_date, {}).values())
    
    def reset_stats(self, short_code: str = None) -> None:
        """
        Reset statistics for a specific short code or all statistics.
        
        Args:
            short_code: Optional short code to reset. If None, resets all statistics.
            
        Example:
            >>> tracker = StatsTracker()
            >>> tracker.track_click("abc123")
            >>> tracker.track_click("xyz789")
            >>> tracker.reset_stats("abc123")
            >>> tracker.get_click_count("abc123")
            0
            >>> tracker.get_click_count("xyz789")
            1
        """
        with self._lock:
            if short_code:
                # Reset specific short code
                if short_code in self._clicks:
                    del self._clicks[short_code]
                for daily_clicks in self._daily_clicks.values():
                    if short_code in daily_clicks:
                        del daily_clicks[short_code]
            else:
                # Reset all statistics
                self._clicks.clear()
                self._daily_clicks.clear()


# Global singleton instance for convenience
_global_tracker = StatsTracker()


def get_global_tracker() -> StatsTracker:
    """
    Get the global StatsTracker singleton instance.
    
    Provides a convenient way to access a shared tracker instance
    across the application.
    
    Returns:
        The global StatsTracker instance
        
    Example:
        >>> from pyshort.stats import track_click, get_global_tracker
        >>> track_click("abc123")
        >>> get_global_tracker().get_click_count("abc123")
        1
    """
    return _global_tracker


# Convenience functions that use the global tracker
def track_click(short_code: str, click_date: date = None) -> None:
    """
    Track a click using the global StatsTracker instance.
    
    This is a convenience function that uses the global tracker.
    See StatsTracker.track_click() for more details.
    
    Args:
        short_code: The short code identifier for the URL
        click_date: Optional date for the click. Defaults to today.
    """
    _global_tracker.track_click(short_code, click_date)


def get_click_count(short_code: str) -> int:
    """
    Get click count using the global StatsTracker instance.
    
    This is a convenience function that uses the global tracker.
    See StatsTracker.get_click_count() for more details.
    
    Args:
        short_code: The short code identifier for the URL
        
    Returns:
        Total number of clicks for the short code, or 0 if not found
    """
    return _global_tracker.get_click_count(short_code)


def get_daily_stats(start_date: date = None, end_date: date = None) -> Dict[date, Dict[str, int]]:
    """
    Get daily statistics using the global StatsTracker instance.
    
    This is a convenience function that uses the global tracker.
    See StatsTracker.get_daily_stats() for more details.
    
    Args:
        start_date: Optional start date (inclusive)
        end_date: Optional end date (inclusive)
        
    Returns:
        Dictionary mapping dates to {short_code: click_count} dictionaries
    """
    return _global_tracker.get_daily_stats(start_date, end_date)


def get_top_urls(limit: int = 10, min_clicks: int = 1) -> List[Tuple[str, int]]:
    """
    Get top URLs using the global StatsTracker instance.
    
    This is a convenience function that uses the global tracker.
    See StatsTracker.get_top_urls() for more details.
    
    Args:
        limit: Maximum number of URLs to return. Use 0 for unlimited.
        min_clicks: Minimum number of clicks required to be included.
        
    Returns:
        List of (short_code, click_count) tuples, sorted by click count descending
    """
    return _global_tracker.get_top_urls(limit, min_clicks)