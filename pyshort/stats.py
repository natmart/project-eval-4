"""
Statistics tracking for the pyshort URL shortener
"""
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional


class StatsTracker:
    """
    Tracks statistics for URL shortening operations.
    
    This includes:
    - Total URLs created
    - Total clicks
    - Clicks per URL
    - URLs created per day
    - Clicks per day
    """
    
    def __init__(self):
        """Initialize a new statistics tracker."""
        self._total_urls_created: int = 0
        self._total_clicks: int = 0
        self._clicks_by_code: Dict[str, int] = defaultdict(int)
        self._urls_created_by_date: Dict[str, int] = defaultdict(int)
        self._clicks_by_date: Dict[str, int] = defaultdict(int)
    
    def record_url_created(self, short_code: str, created_at: Optional[datetime] = None) -> None:
        """
        Record that a new URL was created.
        
        Args:
            short_code: The short code of the created URL
            created_at: The datetime when the URL was created (default: now)
        """
        if created_at is None:
            created_at = datetime.now()
        
        self._total_urls_created += 1
        
        # Track by date (YYYY-MM-DD)
        date_key = created_at.strftime('%Y-%m-%d')
        self._urls_created_by_date[date_key] += 1
    
    def record_click(self, short_code: str, clicked_at: Optional[datetime] = None) -> None:
        """
        Record that a short URL was clicked.
        
        Args:
            short_code: The short code that was clicked
            clicked_at: The datetime when the click occurred (default: now)
        """
        if clicked_at is None:
            clicked_at = datetime.now()
        
        self._total_clicks += 1
        self._clicks_by_code[short_code] += 1
        
        # Track by date (YYYY-MM-DD)
        date_key = clicked_at.strftime('%Y-%m-%d')
        self._clicks_by_date[date_key] += 1
    
    def get_stats(self) -> Dict:
        """
        Get overall statistics.
        
        Returns:
            Dictionary containing overall statistics
        """
        return {
            'total_urls_created': self._total_urls_created,
            'total_clicks': self._total_clicks,
            'unique_urls_with_clicks': len(self._clicks_by_code),
        }
    
    def get_url_stats(self, short_code: str) -> Dict:
        """
        Get statistics for a specific URL.
        
        Args:
            short_code: The short code to get stats for
            
        Returns:
            Dictionary containing statistics for the URL
        """
        return {
            'short_code': short_code,
            'clicks': self._clicks_by_code.get(short_code, 0),
        }
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """
        Get daily statistics for the last N days.
        
        Args:
            days: Number of days to include (default: 7)
            
        Returns:
            List of daily statistics, most recent first
        """
        stats = []
        for i in range(days):
            date = datetime.now().date()
            # Go back i days
            from datetime import timedelta
            target_date = date - timedelta(days=i)
            date_key = target_date.strftime('%Y-%m-%d')
            
            stats.append({
                'date': date_key,
                'urls_created': self._urls_created_by_date.get(date_key, 0),
                'clicks': self._clicks_by_date.get(date_key, 0),
            })
        
        return stats
    
    def get_top_urls(self, limit: int = 10) -> List[Dict]:
        """
        Get the most-clicked URLs.
        
        Args:
            limit: Maximum number of URLs to return (default: 10)
            
        Returns:
            List of URLs with click counts, sorted by clicks (highest first)
        """
        # Sort by click count (descending)
        sorted_urls = sorted(
            self._clicks_by_code.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'short_code': code, 'clicks': count}
            for code, count in sorted_urls[:limit]
        ]
    
    def reset(self) -> None:
        """Reset all statistics to zero."""
        self._total_urls_created = 0
        self._total_clicks = 0
        self._clicks_by_code.clear()
        self._urls_created_by_date.clear()
        self._clicks_by_date.clear()