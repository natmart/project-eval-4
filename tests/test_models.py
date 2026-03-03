"""
Unit tests for the models module.
"""
import pytest
from datetime import datetime, timedelta
from pyshort import ShortURL, validate_url, InvalidURLError


class TestURLValidation:
    """Test cases for URL validation."""
    
    def test_valid_urls(self):
        """Test that valid URLs are correctly validated."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://example.com/path",
            "https://example.com/path?query=value",
            "https://example.com:8080/path",
            "https://sub.example.com",
            "https://example.co.uk",
            "ftp://example.com",
        ]
        
        for url in valid_urls:
            assert validate_url(url), f"{url} should be valid"
    
    def test_invalid_urls(self):
        """Test that invalid URLs are correctly rejected."""
        invalid_urls = [
            "not-a-url",
            "example.com",
            "/path/to/resource",
            "javascript:void(0)",
            "data:text/plain,hello",
            "",
            "mailto:user@example.com",
        ]
        
        for url in invalid_urls:
            assert not validate_url(url), f"{url} should be invalid"


class TestShortURLCreation:
    """Test cases for ShortURL object creation."""
    
    def test_shorturl_creation_with_all_fields(self):
        """Test creating a ShortURL object with all fields populated."""
        now = datetime.now()
        expires = now + timedelta(days=7)
        
        short_url = ShortURL(
            original_url="https://example.com/very/long/path",
            short_code="abc123",
            created_at=now,
            click_count=5,
            expires_at=expires
        )
        
        assert short_url.original_url == "https://example.com/very/long/path"
        assert short_url.short_code == "abc123"
        assert short_url.created_at == now
        assert short_url.click_count == 5
        assert short_url.expires_at == expires
        assert not short_url.is_expired
    
    def test_shorturl_creation_with_defaults(self):
        """Test creating a ShortURL object with default values."""
        now = datetime.now()
        
        short_url = ShortURL(
            original_url="https://example.com",
            short_code="xyz789",
            created_at=now
        )
        
        assert short_url.click_count == 0
        assert short_url.expires_at is None
        assert not short_url.is_expired
    
    def test_shorturl_click_count_increment(self):
        """Test that increment_clicks properly increments the counter."""
        short_url = ShortURL(
            original_url="https://example.com",
            short_code="test",
            created_at=datetime.now()
        )
        
        assert short_url.click_count == 0
        
        short_url.increment_clicks()
        assert short_url.click_count == 1
        
        short_url.increment_clicks()
        short_url.increment_clicks()
        assert short_url.click_count == 3


class TestEdgeCases:
    """Test cases for boundary conditions and edge cases."""
    
    def test_invalid_url_raises_error(self):
        """Test that creating ShortURL with invalid URL raises InvalidURLError."""
        with pytest.raises(InvalidURLError) as exc_info:
            ShortURL(
                original_url="not-a-valid-url",
                short_code="abc",
                created_at=datetime.now()
            )
        assert "Invalid URL" in str(exc_info.value)
    
    def test_empty_short_code_raises_error(self):
        """Test that creating ShortURL with empty short_code raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ShortURL(
                original_url="https://example.com",
                short_code="",
                created_at=datetime.now()
            )
        assert "short_code cannot be empty" in str(exc_info.value)
    
    def test_negative_click_count_raises_error(self):
        """Test that creating ShortURL with negative click_count raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ShortURL(
                original_url="https://example.com",
                short_code="abc",
                created_at=datetime.now(),
                click_count=-1
            )
        assert "click_count cannot be negative" in str(exc_info.value)
    
    def test_expired_url_detection(self):
        """Test that is_expired correctly identifies expired URLs."""
        now = datetime.now()
        past = now - timedelta(days=1)
        future = now + timedelta(days=1)
        
        expired_url = ShortURL(
            original_url="https://example.com",
            short_code="expired",
            created_at=now,
            expires_at=past
        )
        assert expired_url.is_expired
        
        valid_url = ShortURL(
            original_url="https://example.com",
            short_code="valid",
            created_at=now,
            expires_at=future
        )
        assert not valid_url.is_expired
    
    def test_never_expiring_url(self):
        """Test that URL without expires_at never expires."""
        short_url = ShortURL(
            original_url="https://example.com",
            short_code="forever",
            created_at=datetime.now()
        )
        
        assert short_url.expires_at is None
        assert not short_url.is_expired
    
    def test_zero_click_count(self):
        """Test that zero is a valid click count."""
        short_url = ShortURL(
            original_url="https://example.com",
            short_code="test",
            created_at=datetime.now(),
            click_count=0
        )
        
        assert short_url.click_count == 0
        short_url.increment_clicks()
        assert short_url.click_count == 1
    
    def test_expiration_at_exact_time(self):
        """Test URL expiration at the exact expiration boundary."""
        now = datetime.now()
        # Set expiration to 1 millisecond in the past
        expires_past = now - timedelta(milliseconds=1)
        
        short_url = ShortURL(
            original_url="https://example.com",
            short_code="boundary",
            created_at=now,
            expires_at=expires_past
        )
        
        assert short_url.is_expired
    
    def test_various_schemes(self):
        """Test that multiple URL schemes are accepted."""
        schemes = ["https", "http", "ftp"]
        now = datetime.now()
        
        for scheme in schemes:
            url = f"{scheme}://example.com"
            short_url = ShortURL(
                original_url=url,
                short_code=f"test_{scheme}",
                created_at=now
            )
            assert short_url.original_url == url
    
    def test_long_url_handling(self):
        """Test that very long URLs are handled correctly."""
        long_path = "/a" * 1000
        long_url = f"https://example.com{long_path}"
        
        short_url = ShortURL(
            original_url=long_url,
            short_code="long",
            created_at=datetime.now()
        )
        
        assert short_url.original_url == long_url
        assert len(short_url.original_url) > 2000