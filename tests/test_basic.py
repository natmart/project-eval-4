"""
Basic tests to verify project setup
"""
import pytest
from datetime import datetime, timedelta
from pyshort import __version__
from pyshort.models import ShortURL, validate_url


def test_import():
    """Test that we can import the pyshort package"""
    assert __version__ == "0.1.0"


def test_simple_math():
    """A simple test to verify pytest is working"""
    assert 1 + 1 == 2


def test_validate_url_valid():
    """Test URL validation with valid URLs"""
    assert validate_url("https://example.com") is True
    assert validate_url("http://example.com") is True
    assert validate_url("https://example.com/path") is True
    assert validate_url("https://example.com/path?query=value") is True
    assert validate_url("https://example.com:8080/path") is True
    assert validate_url("ftp://example.com") is True


def test_validate_url_invalid():
    """Test URL validation with invalid URLs"""
    assert validate_url("not-a-url") is False
    assert validate_url("") is False
    assert validate_url("example.com") is False  # Missing scheme
    assert validate_url("//example.com") is False  # Missing scheme
    assert validate_url("https://") is False  # No netloc


def test_shorturl_creation():
    """Test creating a ShortURL instance"""
    url = ShortURL(
        original_url="https://example.com/long/path",
        short_code="abc123",
        created_at=datetime.now(),
        click_count=0
    )
    assert url.original_url == "https://example.com/long/path"
    assert url.short_code == "abc123"
    assert url.click_count == 0
    assert url.expires_at is None


def test_shorturl_with_expiration():
    """Test creating a ShortURL with expiration date"""
    expires = datetime.now() + timedelta(days=7)
    url = ShortURL(
        original_url="https://example.com",
        short_code="xyz789",
        created_at=datetime.now(),
        expires_at=expires
    )
    assert url.expires_at == expires
    assert url.is_expired is False


def test_shorturl_expired():
    """Test expired URL detection"""
    expires = datetime.now() - timedelta(days=1)
    url = ShortURL(
        original_url="https://example.com",
        short_code="expired",
        created_at=datetime.now() - timedelta(days=2),
        expires_at=expires
    )
    assert url.is_expired is True


def test_shorturl_no_expiration_never_expires():
    """Test that URLs without expiration never expire"""
    url = ShortURL(
        original_url="https://example.com",
        short_code="forever",
        created_at=datetime.now()
    )
    assert url.is_expired is False


def test_shorturl_increment_clicks():
    """Test incrementing click count"""
    url = ShortURL(
        original_url="https://example.com",
        short_code="clicks",
        created_at=datetime.now(),
        click_count=0
    )
    assert url.click_count == 0
    
    url.increment_clicks()
    assert url.click_count == 1
    
    url.increment_clicks()
    assert url.click_count == 2


def test_shorturl_invalid_url_raises_error():
    """Test that creating ShortURL with invalid URL raises ValueError"""
    with pytest.raises(ValueError, match="Invalid URL"):
        ShortURL(
            original_url="not-a-valid-url",
            short_code="invalid",
            created_at=datetime.now()
        )


def test_shorturl_empty_code_raises_error():
    """Test that creating ShortURL with empty short code raises ValueError"""
    with pytest.raises(ValueError, match="short_code cannot be empty"):
        ShortURL(
            original_url="https://example.com",
            short_code="",
            created_at=datetime.now()
        )


def test_shorturl_negative_clicks_raises_error():
    """Test that creating ShortURL with negative clicks raises ValueError"""
    with pytest.raises(ValueError, match="click_count cannot be negative"):
        ShortURL(
            original_url="https://example.com",
            short_code="negative",
            created_at=datetime.now(),
            click_count=-1
        )


def test_shorturl_repr():
    """Test string representation of ShortURL"""
    url = ShortURL(
        original_url="https://example.com",
        short_code="repr",
        created_at=datetime.now(),
        click_count=42
    )
    repr_str = repr(url)
    assert "ShortURL" in repr_str
    assert "https://example.com" in repr_str
    assert "repr" in repr_str
    assert "click_count=42" in repr_str


def test_shorturl_type_hints():
    """Test that ShortURL has proper type hints"""
    from typing import get_type_hints
    
    hints = get_type_hints(ShortURL)
    assert hints["original_url"] == str
    assert hints["short_code"] == str
    assert hints["created_at"] == datetime
    assert hints["click_count"] == int
    
    from typing import Optional
    # Optional[datetime] is Union[datetime, None]
    assert hints["expires_at"] == Optional[datetime]