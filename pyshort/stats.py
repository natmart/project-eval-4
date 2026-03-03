"""
Statistics tracking for the pyshort URL shortener
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


@dataclass
class URLStats:
    """
    Statistics for a single URL.
    
    Attributes:
        short_code: The short code of the URL
        click_count: Total number of clicks
        created_at: When the URL was created
        last_clicked_at: When the URL was last clicked (None if never clicked)
    """
    short_code: str
    click_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_clicked_at: Optional[datetime] = None
    
    def record_click(self) -> None:
        """Record a click event."""
        self.click_count += 1
        self.last_clicked_at = datetime.now()


class StatsTracker:
    """
    Tracks statistics for shortened URLs.
    
    This includes click counts, creation times, and daily statistics.
    """
    
    def __init__(self):
        """Initialize an empty stats tracker."""
        self._stats: Dict[str, URLStats] = {}
        self._daily_stats: Dict[str, int] = defaultdict(int)
    
    def record_url_created(self, short_code: str) -> None:
        """
        Record that a URL was created.
        
        Args:
            short_code: The short code of the created URL
        """
        if short_code not in self._stats:
            self._stats[short_code] = URLStats(short_code=short_code)
    
    def record_click(self, short_code: str) -> None:
        """
        Record a click event for a URL.
        
        Args:
            short_code: The short code that was clicked
        """
        if short_code not in self._stats:
            self._stats[short_code] = URLStats(short_code=short_code)
        
        self._stats[short_code].record_click()
        
        # Track daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        self._daily_stats[today] += 1
    
    def get_stats(self, short_code: Optional[str] = None) -> Dict:
        """
        Get statistics for a specific URL or overall stats.
        
        Args:
            short_code: Optional short code to get URL-specific stats.
                       If None, returns overall statistics.
        
        Returns:
            Dictionary containing the requested statistics
        """
        if short_code:
            return self._get_url_stats(short_code)
        return self._get_overall_stats()
    
    def _get_url_stats(self, short_code: str) -> Dict:
        """
        Get statistics for a specific URL.
        
        Args:
            short_code: The short code to get stats for
            
        Returns:
            Dictionary with URL statistics
        """
        if short_code not in self._stats:
            return {
                "short_code": short_code,
                "click_count": 0,
                "created_at": None,
                "last_clicked_at": None,
            }
        
        stats = self._stats[short_code]
        return {
            "short_code": stats.short_code,
            "click_count": stats.click_count,
            "created_at": stats.created_at.isoformat() if stats.created_at else None,
            "last_clicked_at": stats.last_clicked_at.isoformat() 
            if stats.last_clicked_at else None,
        }
    
    def _get_overall_stats(self) -> Dict:
        """
        Get overall statistics for all URLs.
        
        Returns:
            Dictionary with overall statistics
        """
        total_clicks = sum(s.click_count for s in self._stats.values())
        
        return {
            "total_urls": len(self._stats),
            "total_clicks": total_clicks,
            "avg_clicks_per_url": total_clicks / len(self._stats) if self._stats else 0,
        }
    
    def get_url_stats(self, short_code: str) -> Optional[Dict]:
        """
        Get detailed statistics for a specific URL.
        
        Args:
            short_code: The short code to get stats for
            
        Returns:
            Dictionary with URL statistics or None if not found
        """
        if short_code not in self._stats:
            return None
        return self._get_url_stats(short_code)
    
    def get_daily_stats(self) -> Dict[str, int]:
        """
        Get click statistics grouped by day.
        
        Returns:
            Dictionary mapping dates to click counts
        """
        return dict(self._daily_stats)
    
    def get_top_urls(self, limit: int = 5) -> List[Dict]:
        """
        Get the top URLs by click count.
        
        Args:
            limit: Maximum number of URLs to return (default: 5)
            
        Returns:
            List of dictionaries containing short_code and click_count,
            sorted by click_count descending
        """
        sorted_urls = sorted(
            self._stats.values(), 
            key=lambda s: s.click_count, 
            reverse=True
        )
        return [
            {
                "short_code": s.short_code,
                "click_count": s.click_count,
            }
            for s in sorted_urls[:limit]
        ]
    
    def reset(self) -> None:
        """Reset all statistics."""
        self._stats.clear()
        self._daily_stats.clear()