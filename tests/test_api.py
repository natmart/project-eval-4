"""
Tests for the main URLShortener API
"""
from datetime import datetime, timedelta
import pytest
from pyshort.api import URLShortener
from pyshort.validator import DEFAULT_BLOCKED_DOMAINS


class TestURLShortenerShorten:
    """Test the shorten() method."""
    
    def test_shorten_basic_url(self):
        """Test basic URL shortening."""
        shortener = URLShortener()
        short_code = shortener.shorten("https://example.com/some/path")
        
        assert short_code is not None
        assert isinstance(short_code, str)
        assert len(short_code) == 6  # default length
        assert shortener.exists(short_code)
    
    def test_shorten_with_custom_code(self):
        """Test shortening with a custom code."""
        shortener = URLShortener()
        short_code = shortener.shorten("https://example.com", custom_code="mylink")
        
        assert short_code == "mylink"
        assert shortener.exists(short_code)
        assert shortener.resolve(short_code) == "https://example.com"
    
    def test_shorten_with_custom_code_invalid(self):
        """Test that invalid custom codes are rejected."""
        shortener = URLShortener()
        
        # Empty code
        with pytest.raises(ValueError, match="custom code cannot be empty"):
            shortener.shorten("https://example.com", custom_code="")
        
        # Invalid characters
        with pytest.raises(ValueError, match="can only contain alphanumeric"):
            shortener.shorten("https://example.com", custom_code="my link!")
    
    def test_shorten_duplicate_code(self):
        """Test that duplicate codes are rejected."""
        shortener = URLShortener()
        
        # Create first URL
        shortener.shorten("https://example.com/first", custom_code="link1")
        
        # Try to create second URL with same code
        with pytest.raises(ValueError, match="already exists"):
            shortener.shorten("https://example.com/second", custom_code="link1")
    
    def test_shorten_normalizes_url(self):
        """Test that URLs are normalized."""
        shortener = URLShortener()
        short_code = shortener.shorten("EXAMPLE.COM")
        
        original = shortener.resolve(short_code)
        assert original == "https://example.com"
    
    def test_shorten_blocks_malicious_domain(self):
        """Test that blocked domains are rejected."""
        shortener = URLShortener()
        
        with pytest.raises(ValueError, match="Domain is blocked"):
            shortener.shorten("https://malicious-site.com")
    
    def test_shorten_with_custom_blocked_domains(self):
        """Test shortening with custom blocked domains."""
        shortener = URLShortener(blocked_domains={"bad-example.com"})
        
        # Should work
        shortener.shorten("https://good-example.com")
        
        # Should be blocked
        with pytest.raises(ValueError, match="Domain is blocked"):
            shortener.shorten("https://bad-example.com")
    
    def test_shorten_with_expiration(self):
        """Test shortening with expiration."""
        shortener = URLShortener()
        expires = datetime.now() + timedelta(hours=1)
        
        short_code = shortener.shorten("https://example.com", expires_at=expires)
        stats = shortener.get_stats(short_code)
        
        assert stats['expires_at'] is not None
        assert not stats['is_expired']
    
    def test_shorten_with_ttl_days(self):
        """Test shortening with TTL in days."""
        shortener = URLShortener()
        
        short_code = shortener.shorten("https://example.com", ttl_days=7)
        stats = shortener.get_stats(short_code)
        
        assert stats['expires_at'] is not None
        
        # Check expiration is approximately 7 days from now
        expires_at = datetime.fromisoformat(stats['expires_at'])
        assert expires_at > datetime.now() + timedelta(days=6)
        assert expires_at < datetime.now() + timedelta(days=8)
    
    def test_shorten_with_default_ttl(self):
        """Test shortening with default TTL."""
        shortener = URLShortener(default_ttl_days=30)
        
        short_code = shortener.shorten("https://example.com")
        stats = shortener.get_stats(short_code)
        
        assert stats['expires_at'] is not None
    
    def test_shorten_custom_code_length(self):
        """Test shortening with custom code length."""
        shortener = URLShortener()
        short_code = shortener.shorten("https://example.com", code_length=10)
        
        assert len(short_code) == 10


class TestURLShortenerResolve:
    """Test the resolve() method."""
    
    def test_resolve_existing_url(self):
        """Test resolving an existing short URL."""
        shortener = URLShortener()
        original = "https://example.com/test"
        short_code = shortener.shorten(original)
        
        resolved = shortener.resolve(short_code)
        assert resolved == "https://example.com/test"
    
    def test_resolve_nonexistent_url(self):
        """Test resolving a non-existent short URL."""
        shortener = URLShortener()
        
        resolved = shortener.resolve("nonexistent")
        assert resolved is None
    
    def test_resolve_expired_url(self):
        """Test resolving an expired URL."""
        shortener = URLShortener()
        # Create an already expired URL
        expires = datetime.now() - timedelta(hours=1)
        short_code = shortener.shorten("https://example.com", expires_at=expires)
        
        resolved = shortener.resolve(short_code)
        assert resolved is None
    
    def test_resolve_increments_click_count(self):
        """Test that resolving increments the click count."""
        shortener = URLShortener()
        short_code = shortener.shorten("https://example.com")
        
        # First resolve
        shortener.resolve(short_code)
        stats1 = shortener.get_stats(short_code)
        
        # Second resolve
        shortener.resolve(short_code)
        stats2 = shortener.get_stats(short_code)
        
        # Storage count should be higher
        all_urls = shortener.get_all_urls()
        url_info = [u for u in all_urls if u['short_code'] == short_code][0]
        
        assert url_info['click_count'] == 2


class TestURLShortenerGetStats:
    """Test the get_stats() method."""
    
    def test_get_overall_stats(self):
        """Test getting overall statistics."""
        shortener = URLShortener()
        
        # Create some URLs
        shortener.shorten("https://example.com/1")
        shortener.shorten("https://example.com/2")
        
        stats = shortener.get_stats()
        
        assert stats['total_urls_created'] == 2
        assert stats['total_urls_in_storage'] == 2
        assert stats['total_clicks'] == 0
    
    def test_get_url_stats(self):
        """Test getting stats for a specific URL."""
        shortener = URLShortener()
        short_code = shortener.shorten("https://example.com/test")
        
        # Click the URL a few times
        shortener.resolve(short_code)
        shortener.resolve(short_code)
        
        stats = shortener.get_stats(short_code)
        
        assert stats['short_code'] == short_code
        assert stats['original_url'] == "https://example.com/test"
        assert stats['clicks'] == 2
        assert 'created_at' in stats
        assert 'is_expired' in stats
    
    def test_get_stats_nonexistent_url(self):
        """Test getting stats for a non-existent URL."""
        shortener = URLShortener()
        stats = shortener.get_stats("nonexistent")
        
        assert stats['short_code'] == "nonexistent"
        assert stats['clicks'] == 0
        assert 'original_url' not in stats


class TestURLShortenerDelete:
    """Test the delete() method."""
    
    def test_delete_existing_url(self):
        """Test deleting an existing URL."""
        shortener = URLShortener()
        short_code = shortener.shorten("https://example.com")
        
        assert shortener.exists(short_code)
        
        result = shortener.delete(short_code)
        
        assert result is True
        assert not shortener.exists(short_code)
    
    def test_delete_nonexistent_url(self):
        """Test deleting a non-existent URL."""
        shortener = URLShortener()
        
        result = shortener.delete("nonexistent")
        assert result is False
    
    def test_delete_and_resolve(self):
        """Test that deleted URLs cannot be resolved."""
        shortener = URLShortener()
        short_code = shortener.shorten("https://example.com")
        
        shortener.delete(short_code)
        
        resolved = shortener.resolve(short_code)
        assert resolved is None


class TestURLShortenerExists:
    """Test the exists() method."""
    
    def test_exists_true(self):
        """Test exists() with an existing code."""
        shortener = URLShortener()
        short_code = shortener.shorten("https://example.com")
        
        assert shortener.exists(short_code) is True
    
    def test_exists_false(self):
        """Test exists() with a non-existent code."""
        shortener = URLShortener()
        
        assert shortener.exists("nonexistent") is False


class TestURLShortenerGetAllURLs:
    """Test the get_all_urls() method."""
    
    def test_get_all_urls_empty(self):
        """Test getting all URLs when none exist."""
        shortener = URLShortener()
        
        urls = shortener.get_all_urls()
        assert urls == []
    
    def test_get_all_urls_multiple(self):
        """Test getting all URLs with multiple entries."""
        shortener = URLShortener()
        
        code1 = shortener.shorten("https://example.com/1")
        code2 = shortener.shorten("https://example.com/2")
        code3 = shortener.shorten("https://example.com/3")
        
        # Click first URL twice
        shortener.resolve(code1)
        shortener.resolve(code1)
        # Click second URL once
        shortener.resolve(code2)
        
        urls = shortener.get_all_urls()
        
        assert len(urls) == 3
        
        # Check they all have required fields
        for url_info in urls:
            assert 'short_code' in url_info
            assert 'original_url' in url_info
            assert 'created_at' in url_info
            assert 'click_count' in url_info
            assert 'is_expired' in url_info


class TestURLShortenerDailyStats:
    """Test the get_daily_stats() method."""
    
    def test_get_daily_stats(self):
        """Test getting daily statistics."""
        shortener = URLShortener()
        
        # Create and click some URLs
        code1 = shortener.shorten("https://example.com/1")
        code2 = shortener.shorten("https://example.com/2")
        
        shortener.resolve(code1)
        shortener.resolve(code1)
        shortener.resolve(code2)
        
        daily_stats = shortener.get_daily_stats(days=1)
        
        assert len(daily_stats) == 1
        assert daily_stats[0]['urls_created'] == 2
        assert daily_stats[0]['clicks'] == 3


class TestURLShortenerTopURLs:
    """Test the get_top_urls() method."""
    
    def test_get_top_urls_empty(self):
        """Test getting top URLs when none exist."""
        shortener = URLShortener()
        
        top_urls = shortener.get_top_urls()
        assert top_urls == []
    
    def test_get_top_urls_ordered(self):
        """Test that top URLs are ordered by clicks."""
        shortener = URLShortener()
        
        code1 = shortener.shorten("https://example.com/1")
        code2 = shortener.shorten("https://example.com/2")
        code3 = shortener.shorten("https://example.com/3")
        
        # Click different amounts
        for _ in range(5):
            shortener.resolve(code1)
        for _ in range(3):
            shortener.resolve(code2)
        for _ in range(1):
            shortener.resolve(code3)
        
        top_urls = shortener.get_top_urls()
        
        assert len(top_urls) == 3
        assert top_urls[0]['short_code'] == code1
        assert top_urls[0]['clicks'] == 5
        assert top_urls[1]['short_code'] == code2
        assert top_urls[1]['clicks'] == 3


class TestURLShortenerCleanupExpired:
    """Test the cleanup_expired() method."""
    
    def test_cleanup_expired(self):
        """Test cleaning up expired URLs."""
        shortener = URLShortener()
        
        # Create an expired URL
        expires = datetime.now() - timedelta(hours=1)
        expired_code = shortener.shorten("https://example.com/expired", expires_at=expires)
        
        # Create a non-expired URL
        valid_code = shortener.shorten("https://example.com/valid")
        
        assert shortener.exists(expired_code)
        assert shortener.exists(valid_code)
        
        removed = shortener.cleanup_expired()
        
        assert removed == 1
        assert not shortener.exists(expired_code)
        assert shortener.exists(valid_code)
    
    def test_cleanup_expired_none(self):
        """Test cleanup when no expired URLs exist."""
        shortener = URLShortener()
        
        shortener.shorten("https://example.com/1")
        shortener.shorten("https://example.com/2")
        
        removed = shortener.cleanup_expired()
        
        assert removed == 0


class TestURLShortenerIntegration:
    """Integration tests for the full URL shortener workflow."""
    
    def test_full_workflow(self):
        """Test a complete workflow: shorten, resolve, stats, delete."""
        shortener = URLShortener()
        
        # 1. Create a short URL
        code = shortener.shorten("https://example.com/my-long-url-path")
        assert shortener.exists(code)
        
        # 2. Resolve it
        original = shortener.resolve(code)
        assert original == "https://example.com/my-long-url-path"
        
        # 3. Get stats
        stats = shortener.get_stats(code)
        assert stats['clicks'] == 1
        assert stats['original_url'] == "https://example.com/my-long-url-path"
        
        # 4. Delete it
        deleted = shortener.delete(code)
        assert deleted is True
        assert not shortener.exists(code)
    
    def test_multiple_urls_workflow(self):
        """Test workflow with multiple URLs."""
        shortener = URLShortener()
        
        codes = []
        for i in range(5):
            code = shortener.shorten(f"https://example.com/page{i}")
            codes.append(code)
        
        # Verify all exist
        for code in codes:
            assert shortener.exists(code)
        
        # Resolve all
        for code in codes:
            shortener.resolve(code)
        
        # Check overall stats
        stats = shortener.get_stats()
        assert stats['total_urls_created'] == 5
        assert stats['total_clicks'] == 5
        
        # Get all URLs
        all_urls = shortener.get_all_urls()
        assert len(all_urls) == 5
        
        # Delete all
        for code in codes:
            assert shortener.delete(code) is True
        
        # Verify none exist
        for code in codes:
            assert not shortener.exists(code)