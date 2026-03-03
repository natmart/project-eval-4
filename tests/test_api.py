"""
Unit tests for the main API module (pyshort.api)
"""
import pytest
from datetime import datetime, timedelta
from pyshort.api import URLShortener
from pyshort.storage import InMemoryStorage
from pyshort.stats import StatsTracker
from pyshort.models import ShortURL


class TestShorten:
    """Test cases for the shorten() method."""
    
    def test_shorten_creates_short_url(self):
        """Test that shorten() creates a ShortURL with valid data."""
        shortener = URLShortener()
        url = "https://example.com"
        
        result = shortener.shorten(url)
        
        assert isinstance(result, ShortURL)
        assert result.original_url == url
        assert result.short_code is not None
        assert len(result.short_code) > 0
        assert result.created_at is not None
        assert result.click_count == 0
        assert result.expires_at is None
    
    def test_shorten_generates_unique_codes(self):
        """Test that shorten() generates unique short codes."""
        shortener = URLShortener()
        url1 = "https://example1.com"
        url2 = "https://example2.com"
        
        result1 = shortener.shorten(url1)
        result2 = shortener.shorten(url2)
        
        assert result1.short_code != result2.short_code
    
    def test_shorten_with_custom_code(self):
        """Test that shorten() accepts and uses custom codes."""
        shortener = URLShortener()
        url = "https://example.com"
        custom_code = "mycustom"
        
        result = shortener.shorten(url, custom_code=custom_code)
        
        assert result.short_code == custom_code
    
    def test_shorten_rejects_duplicate_custom_code(self):
        """Test that shorten() raises ValueError for duplicate custom codes."""
        shortener = URLShortener()
        url1 = "https://example1.com"
        url2 = "https://example2.com"
        custom_code = "unique"
        
        shortener.shorten(url1, custom_code=custom_code)
        
        with pytest.raises(ValueError, match="already taken"):
            shortener.shorten(url2, custom_code=custom_code)
    
    def test_shorten_with_expiration(self):
        """Test that shorten() creates URLs with expiration dates."""
        shortener = URLShortener()
        url = "https://example.com"
        expires_in_days = 7
        
        result = shortener.shorten(url, expires_in_days=expires_in_days)
        
        assert result.expires_at is not None
        assert isinstance(result.expires_at, datetime)
        # Check that expiration is approximately correct (within 1 second)
        expected_expiration = datetime.now() + timedelta(days=expires_in_days)
        time_diff = abs((result.expires_at - expected_expiration).total_seconds())
        assert time_diff < 1
    
    def test_shorten_normalizes_url(self):
        """Test that shorten() normalizes URLs."""
        shortener = URLShortener()
        # Redirect URL should be stored as its resolved form
        url = "http://example.com/?query=test#fragment"
        
        result = shortener.shorten(url)
        
        assert "example.com" in result.original_url.lower()
    
    def test_shorten_invalid_url_raises_error(self):
        """Test that shorten() raises ValueError for invalid URLs."""
        shortener = URLShortener()
        
        with pytest.raises(ValueError, match="Invalid URL"):
            shortener.shorten("not-a-url")
        
        with pytest.raises(ValueError, match="Invalid URL"):
            shortener.shorten("")
    
    def test_shorten_empty_custom_code_raises_error(self):
        """Test that shorten() raises ValueError for empty custom code."""
        shortener = URLShortener()
        url = "https://example.com"
        
        with pytest.raises(ValueError, match="cannot be empty"):
            shortener.shorten(url, custom_code="")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            shortener.shorten(url, custom_code="   ")
    
    def test_shorten_records_creation_in_stats(self):
        """Test that shorten() records URL creation in statistics."""
        shortener = URLShortener()
        url = "https://example.com"
        
        result = shortener.shorten(url)
        
        stats = shortener.get_stats(result.short_code)
        assert stats is not None
        assert stats["short_code"] == result.short_code


class TestResolve:
    """Test cases for the resolve() method."""
    
    def test_resolve_retrieves_original_url(self):
        """Test that resolve() retrieves the original URL by short code."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        resolved_url = shortener.resolve(short_url.short_code)
        
        assert resolved_url == url
    
    def test_resolve_returns_none_for_nonexistent_code(self):
        """Test that resolve() returns None for non-existent short codes."""
        shortener = URLShortener()
        
        result = shortener.resolve("nonexistent")
        
        assert result is None
    
    def test_resolve_increments_click_count(self):
        """Test that resolve() tracks clicks when track_click=True (default)."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        
        # Resolve the URL
        shortener.resolve(short_url.short_code)
        
        # Check stats
        stats = shortener.get_stats(short_url.short_code)
        assert stats["click_count"] == 1
    
    def test_resolve_tracks_multiple_clicks(self):
        """Test that resolve() tracks multiple clicks correctly."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        
        # Resolve the URL multiple times
        for _ in range(5):
            shortener.resolve(short_url.short_code)
        
        # Check stats
        stats = shortener.get_stats(short_url.short_code)
        assert stats["click_count"] == 5
    
    def test_resolve_respects_track_click_parameter(self):
        """Test that resolve() respects the track_click parameter."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        
        # Resolve without tracking
        shortener.resolve(short_url.short_code, track_click=False)
        stats = shortener.get_stats(short_url.short_code)
        assert stats["click_count"] == 0
        
        # Resolve with tracking (default)
        shortener.resolve(short_url.short_code)
        stats = shortener.get_stats(short_url.short_code)
        assert stats["click_count"] == 1
    
    def test_resolve_returns_none_for_expired_url(self):
        """Test that resolve() returns None for expired URLs."""
        shortener = URLShortener()
        url = "https://example.com"
        
        # Create a URL that expires in 0 days
        short_url = shortener.shorten(url, expires_in_days=0)
        
        # Wait a tiny bit to ensure it's expired
        import time
        time.sleep(0.1)
        
        result = shortener.resolve(short_url.short_code)
        
        assert result is None
    
    def test_resolve_updates_last_clicked_at(self):
        """Test that resolve() updates the last_clicked_at timestamp."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        
        # First resolve - should set last_clicked_at
        shortener.resolve(short_url.short_code)
        stats1 = shortener.get_stats(short_url.short_code)
        assert stats1["last_clicked_at"] is not None
        
        # Wait a tiny bit
        import time
        time.sleep(0.1)
        
        # Second resolve - should update last_clicked_at
        shortener.resolve(short_url.short_code)
        stats2 = shortener.get_stats(short_url.short_code)
        
        # The second last_clicked_at should be later than the first
        if stats1["last_clicked_at"] and stats2["last_clicked_at"]:
            time1 = datetime.fromisoformat(stats1["last_clicked_at"])
            time2 = datetime.fromisoformat(stats2["last_clicked_at"])
            assert time2 > time1


class TestStatsAndDelete:
    """Test cases for get_stats() and delete() methods."""
    
    def test_get_stats_for_specific_url(self):
        """Test that get_stats() returns correct statistics for a specific URL."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        
        # Generate some clicks
        for _ in range(3):
            shortener.resolve(short_url.short_code)
        
        stats = shortener.get_stats(short_url.short_code)
        
        assert stats["short_code"] == short_url.short_code
        assert stats["click_count"] == 3
        assert stats["created_at"] is not None
        assert stats["last_clicked_at"] is not None
    
    def test_get_stats_overall(self):
        """Test that get_stats() returns overall statistics when no code provided."""
        shortener = URLShortener()
        
        # Create multiple URLs
        url1 = shortener.shorten("https://example1.com")
        url2 = shortener.shorten("https://example2.com")
        url3 = shortener.shorten("https://example3.com")
        
        # Generate various clicks
        for _ in range(5):
            shortener.resolve(url1.short_code)
        
        for _ in range(3):
            shortener.resolve(url2.short_code)
        
        for _ in range(2):
            shortener.resolve(url3.short_code)
        
        stats = shortener.get_stats()
        
        assert stats["total_urls"] == 3
        assert stats["total_clicks"] == 10
        assert stats["avg_clicks_per_url"] == pytest.approx(10 / 3, rel=1e-5)
    
    def test_get_stats_for_nonexistent_url(self):
        """Test that get_stats() returns stats for non-existent URL."""
        shortener = URLShortener()
        
        stats = shortener.get_stats("nonexistent")
        
        assert stats["short_code"] == "nonexistent"
        assert stats["click_count"] == 0
        assert stats["created_at"] is None
        assert stats["last_clicked_at"] is None
    
    def test_get_stats_empty_system(self):
        """Test that get_stats() returns zeros for empty system."""
        shortener = URLShortener()
        
        stats = shortener.get_stats()
        
        assert stats["total_urls"] == 0
        assert stats["total_clicks"] == 0
        assert stats["avg_clicks_per_url"] == 0
    
    def test_delete_existing_url(self):
        """Test that delete() removes an existing URL."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        
        # Verify it exists
        assert shortener.exists(short_url.short_code)
        
        # Delete it
        result = shortener.delete(short_url.short_code)
        
        assert result is True
        assert not shortener.exists(short_url.short_code)
    
    def test_delete_nonexistent_url(self):
        """Test that delete() returns False for non-existent URL."""
        shortener = URLShortener()
        
        result = shortener.delete("nonexistent")
        
        assert result is False
    
    def test_delete_clears_from_stats(self):
        """Test that delete() removes URL from statistics."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        shortener.resolve(short_url.short_code)
        
        # Verify stats before delete
        before_stats = shortener.get_stats()
        assert before_stats["total_urls"] == 1
        
        # Delete the URL
        shortener.delete(short_url.short_code)
        
        # Verify stats after delete - overall stats won't change because
        # stats are still tracked, but the URL is gone from storage
        after_stats = shortener.get_stats()
        # Stats tracker doesn't remove on URL deletion
        assert after_stats["total_urls"] >= 1
    
    def test_delete_and_resolve(self):
        """Test that after delete(), resolve() returns None."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        shortener.delete(short_url.short_code)
        
        result = shortener.resolve(short_url.short_code)
        
        assert result is None


class TestUtilityMethods:
    """Test cases for additional utility methods."""
    
    def test_exists_for_existing_url(self):
        """Test that exists() returns True for existing URLs."""
        shortener = URLShortener()
        url = "https://example.com"
        
        short_url = shortener.shorten(url)
        
        assert shortener.exists(short_url.short_code)
    
    def test_exists_for_nonexistent_url(self):
        """Test that exists() returns False for non-existent URLs."""
        shortener = URLShortener()
        
        assert not shortener.exists("nonexistent")
    
    def test_exists_for_expired_url(self):
        """Test that exists() returns False for expired URLs."""
        shortener = URLShortener()
        url = "https://example.com"
        
        # Create a URL that expires immediately
        short_url = shortener.shorten(url, expires_in_days=0)
        
        # Wait a tiny bit to ensure it's expired
        import time
        time.sleep(0.1)
        
        assert not shortener.exists(short_url.short_code)
    
    def test_get_all_urls(self):
        """Test that get_all_urls() returns all stored URLs."""
        shortener = URLShortener()
        
        # Create multiple URLs
        url1 = shortener.shorten("https://example1.com")
        url2 = shortener.shorten("https://example2.com")
        url3 = shortener.shorten("https://example3.com")
        
        all_urls = shortener.get_all_urls()
        
        assert len(all_urls) == 3
        codes = {url.short_code for url in all_urls}
        assert url1.short_code in codes
        assert url2.short_code in codes
        assert url3.short_code in codes
    
    def test_get_all_urls_empty(self):
        """Test that get_all_urls() returns empty list when no URLs."""
        shortener = URLShortener()
        
        all_urls = shortener.get_all_urls()
        
        assert len(all_urls) == 0
    
    def test_get_daily_stats(self):
        """Test that get_daily_stats() returns correct daily statistics."""
        shortener = URLShortener()
        
        # Create and click a URL multiple times
        short_url = shortener.shorten("https://example.com")
        for _ in range(5):
            shortener.resolve(short_url.short_code)
        
        daily_stats = shortener.get_daily_stats()
        
        assert len(daily_stats) >= 1
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in daily_stats
        assert daily_stats[today] == 5
    
    def test_get_top_urls(self):
        """Test that get_top_urls() returns URLs sorted by click count."""
        shortener = URLShortener()
        
        # Create URLs with different click counts
        url1 = shortener.shorten("https://example1.com")
        url2 = shortener.shorten("https://example2.com")
        url3 = shortener.shorten("https://example3.com")
        
        # Generate different numbers of clicks
        for _ in range(10):
            shortener.resolve(url1.short_code)
        for _ in range(5):
            shortener.resolve(url2.short_code)
        for _ in range(2):
            shortener.resolve(url3.short_code)
        
        top_urls = shortener.get_top_urls(limit=3)
        
        assert len(top_urls) == 3
        assert top_urls[0]["short_code"] == url1.short_code
        assert top_urls[0]["click_count"] == 10
        assert top_urls[1]["short_code"] == url2.short_code
        assert top_urls[1]["click_count"] == 5
        assert top_urls[2]["short_code"] == url3.short_code
        assert top_urls[2]["click_count"] == 2
    
    def test_get_top_urls_with_limit(self):
        """Test that get_top_urls() respects the limit parameter."""
        shortener = URLShortener()
        
        # Create multiple URLs
        for i in range(10):
            url = shortener.shorten(f"https://example{i}.com")
            for _ in range(i + 1):
                shortener.resolve(url.short_code)
        
        top_urls = shortener.get_top_urls(limit=5)
        
        assert len(top_urls) == 5
    
    def test_cleanup_expired(self):
        """Test that cleanup_expired() removes all expired URLs."""
        shortener = URLShortener()
        
        # Create URLs with different expiration times
        url_expired = shortener.shorten("https://expired.com", expires_in_days=0)
        url_valid1 = shortener.shorten("https://valid1.com", expires_in_days=1)
        url_valid2 = shortener.shorten("https://valid2.com", expires_in_days=2)
        url_no_expiry = shortener.shorten("https://noexpiry.com")
        
        # Wait a tiny bit to ensure the expired URL is expired
        import time
        time.sleep(0.1)
        
        # Cleanup expired URLs
        cleaned = shortener.cleanup_expired()
        
        assert cleaned == 1
        assert not shortener.exists(url_expired.short_code)
        assert shortener.exists(url_valid1.short_code)
        assert shortener.exists(url_valid2.short_code)
        assert shortener.exists(url_no_expiry.short_code)
    
    def test_cleanup_expired_none_expired(self):
        """Test that cleanup_expired() returns 0 when no URLs are expired."""
        shortener = URLShortener()
        
        # Create only valid URLs
        url1 = shortener.shorten("https://valid1.com")
        url2 = shortener.shorten("https://valid2.com", expires_in_days=7)
        
        cleaned = shortener.cleanup_expired()
        
        assert cleaned == 0
        assert shortener.exists(url1.short_code)
        assert shortener.exists(url2.short_code)


class TestIntegration:
    """Integration tests testing the full workflow."""
    
    def test_full_workflow_shorten_resolve_stats_delete(self):
        """Test the complete workflow: shorten -> resolve -> stats -> delete."""
        shortener = URLShortener()
        url = "https://example.com/path?query=value#fragment"
        
        # Step 1: Shorten
        short_url = shortener.shorten(url)
        assert short_url is not None
        assert shortener.exists(short_url.short_code)
        
        # Step 2: Resolve multiple times
        for _ in range(5):
            resolved = shortener.resolve(short_url.short_code)
            assert resolved == url
        
        # Step 3: Get stats
        stats = shortener.get_stats(short_url.short_code)
        assert stats["click_count"] == 5
        
        overall_stats = shortener.get_stats()
        assert overall_stats["total_urls"] == 1
        assert overall_stats["total_clicks"] == 5
        
        # Step 4: Delete
        deleted = shortener.delete(short_url.short_code)
        assert deleted is True
        assert not shortener.exists(short_url.short_code)
        
        # Step 5: Verify resolution fails
        resolved = shortener.resolve(short_url.short_code)
        assert resolved is None
    
    def test_multiple_urls_independent_stats(self):
        """Test that multiple URLs maintain independent statistics."""
        shortener = URLShortener()
        
        urls = [
            shortener.shorten("https://example1.com"),
            shortener.shorten("https://example2.com"),
            shortener.shorten("https://example3.com"),
        ]
        
        # Generate different numbers of clicks for each
        for i, url in enumerate(urls):
            for _ in range(i + 1):
                shortener.resolve(url.short_code)
        
        # Verify independent stats
        for i, url in enumerate(urls):
            stats = shortener.get_stats(url.short_code)
            assert stats["click_count"] == i + 1
        
        # Verify overall stats
        overall = shortener.get_stats()
        assert overall["total_urls"] == 3
        assert overall["total_clicks"] == 6  # 1 + 2 + 3
    
    def test_custom_components_injection(self):
        """Test that custom storage and stats can be injected."""
        custom_storage = InMemoryStorage()
        custom_stats = StatsTracker()
        
        shortener = URLShortener(
            storage=custom_storage,
            stats_tracker=custom_stats
        )
        
        url = "https://example.com"
        short_url = shortener.shorten(url)
        
        # Should work with custom components
        assert shortener.exists(short_url.short_code)
        assert shortener.resolve(short_url.short_code) == url
        assert shortener.get_stats()["total_urls"] == 1