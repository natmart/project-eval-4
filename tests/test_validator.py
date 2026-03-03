"""
Tests for the pyshort validator module.
"""

import pytest
from pyshort.validator import (
    validate_url,
    extract_domain,
    is_domain_blocked,
    normalize_url,
    get_url_components,
    is_url_safe,
    DEFAULT_BLOCKED_DOMAINS,
)


class TestValidateURL:
    """Tests for validate_url function."""
    
    def test_valid_https_url(self):
        """Test validation of valid HTTPS URLs."""
        assert validate_url("https://example.com") is True
        assert validate_url("https://sub.example.com") is True
        assert validate_url("https://example.com/path") is True
        assert validate_url("https://example.com/path?query=value") is True
        assert validate_url("https://example.com:8080") is True
    
    def test_valid_http_url(self):
        """Test validation of valid HTTP URLs."""
        assert validate_url("http://example.com") is True
        assert validate_url("http://sub.example.com/path") is True
    
    def test_invalid_scheme(self):
        """Test that URLs with invalid schemes are rejected."""
        assert validate_url("ftp://example.com") is False
        assert validate_url("file://path/to/file") is False
        assert validate_url("javascript:alert('xss')") is False
        assert validate_url("data:text/plain,hello") is False
    
    def test_custom_allowed_schemes(self):
        """Test custom allowed schemes."""
        assert validate_url("ftp://example.com", allowed_schemes=['http', 'https', 'ftp']) is True
        assert validate_url("https://example.com", allowed_schemes=['http']) is False
        assert validate_url("http://example.com", allowed_schemes=['http', 'ftp']) is True
    
    def test_missing_scheme(self):
        """Test that URLs without scheme are rejected."""
        assert validate_url("example.com") is False
        assert validate_url("www.example.com") is False
        assert validate_url("/path/to/resource") is False
    
    def test_missing_domain(self):
        """Test that URLs without domain are rejected."""
        assert validate_url("http://") is False
        assert validate_url("https:///path") is False
    
    def test_invalid_url_format(self):
        """Test that invalid URL formats are rejected."""
        assert validate_url("") is False
        assert validate_url(None) is False
        assert validate_url(123) is False
        assert validate_url("not-a-url") is False
        assert validate_url("http://") is False
    
    def test_invalid_domain_format(self):
        """Test that invalid domain formats are rejected."""
        assert validate_url("http://..") is False
        assert validate_url("http://.com") is False
        assert validate_url("http://example.") is False
        assert validate_url("http://-example.com") is False
        assert validate_url("http://example-.com") is False
    
    def test_domain_with_invalid_characters(self):
        """Test that domains with invalid characters are rejected."""
        assert validate_url("http://example!.com") is False
        assert validate_url("http://example@com") is False
        assert validate_url("http://example space.com") is False


class TestExtractDomain:
    """Tests for extract_domain function."""
    
    def test_extract_simple_domain(self):
        """Test extracting simple domain."""
        assert extract_domain("https://example.com") == "example.com"
        assert extract_domain("http://example.com/path") == "example.com"
    
    def test_extract_subdomain(self):
        """Test extracting subdomain."""
        assert extract_domain("https://sub.example.com") == "sub.example.com"
        assert extract_domain("https://api.v2.example.com") == "api.v2.example.com"
    
    def test_extract_domain_with_port(self):
        """Test extracting domain with port."""
        assert extract_domain("https://example.com:8080") == "example.com"
        assert extract_domain("http://example.com:443/path") == "example.com"
    
    def test_domain_lowercased(self):
        """Test that domain is lowercased."""
        assert extract_domain("https://EXAMPLE.COM") == "example.com"
        assert extract_domain("https://SuB.ExAmPlE.CoM") == "sub.example.com"
    
    def test_extract_invalid_url(self):
        """Test extracting domain from invalid URLs."""
        assert extract_domain("not-a-url") is None
        assert extract_domain("") is None
        assert extract_domain(None) is None
        assert extract_domain("http:///path") is None
    
    def test_extract_domain_with_query_and_fragment(self):
        """Test extracting domain with query and fragment."""
        assert extract_domain("https://example.com/path?query=value#section") == "example.com"


class TestIsDomainBlocked:
    """Tests for is_domain_blocked function."""
    
    def test_default_blocked_domains(self):
        """Test checking against default blocked domains list."""
        assert is_domain_blocked("https://malicious-site.com") is True
        assert is_domain_blocked("http://spam.example") is True
        assert is_domain_blocked("https://phishing.net/path") is True
    
    def test_custom_blocked_domains(self):
        """Test checking against custom blocked domains."""
        blocked = {"bad.com", "evil.net"}
        assert is_domain_blocked("https://bad.com", blocked_domains=blocked) is True
        assert is_domain_blocked("https://evil.net", blocked_domains=blocked) is True
        assert is_domain_blocked("https://good.com", blocked_domains=blocked) is False
    
    def test_subdomain_blocking(self):
        """Test that subdomains of blocked domains are also blocked."""
        blocked = {"bad.com"}
        assert is_domain_blocked("https://sub.bad.com", blocked_domains=blocked) is True
        assert is_domain_blocked("https://deep.sub.bad.com", blocked_domains=blocked) is True
    
    def test_case_insensitive_default(self):
        """Test that domain blocking is case insensitive by default."""
        assert is_domain_blocked("https://MALICIOUS-SITE.COM") is True
        assert is_domain_blocked("https://Sub.Malicious-Site.Com") is True
    
    def test_case_sensitive(self):
        """Test case sensitive domain blocking."""
        blocked = {"Example.COM"}
        assert is_domain_blocked("https://Example.COM", blocked_domains=blocked, case_sensitive=True) is True
        assert is_domain_blocked("https://example.com", blocked_domains=blocked, case_sensitive=True) is False
    
    def test_invalid_url_not_blocked(self):
        """Test that invalid URLs return False (not blocked)."""
        assert is_domain_blocked("not-a-url") is False
        assert is_domain_blocked("") is False
    
    def test_empty_blocked_list(self):
        """Test with empty blocked domains list."""
        assert is_domain_blocked("https://example.com", blocked_domains=set()) is False
        assert is_domain_blocked("https://malicious-site.com", blocked_domains=set()) is False


class TestNormalizeURL:
    """Tests for normalize_url function."""
    
    def test_add_default_scheme(self):
        """Test adding default HTTPS scheme."""
        assert normalize_url("example.com") == "https://example.com"
        assert normalize_url("example.com/path") == "https://example.com/path"
    
    def test_preserve_existing_scheme(self):
        """Test preserving existing scheme."""
        assert normalize_url("https://example.com") == "https://example.com"
        assert normalize_url("http://example.com") == "http://example.com"
        assert normalize_url("HTTPS://EXAMPLE.COM") == "https://example.com"
        assert normalize_url("HTTP://EXAMPLE.COM") == "http://example.com"
    
    def test_lowercase_domain(self):
        """Test that domain is lowercased."""
        assert normalize_url("https://EXAMPLE.COM") == "https://example.com"
        assert normalize_url("https://SuB.ExAmPlE.CoM") == "https://sub.example.com"
    
    def test_preserve_port(self):
        """Test that port is preserved."""
        assert normalize_url("https://example.com:8080") == "https://example.com:8080"
        assert normalize_url("EXAMPLE.COM:9000") == "https://example.com:9000"
    
    def test_remove_fragment(self):
        """Test that fragment is removed."""
        assert normalize_url("https://example.com#section") == "https://example.com"
        assert normalize_url("https://example.com/path#anchor") == "https://example.com/path"
    
    def test_normalize_trailing_slash(self):
        """Test removing trailing slash from path."""
        assert normalize_url("https://example.com/") == "https://example.com"
        assert normalize_url("https://example.com/path/") == "https://example.com/path"
        assert normalize_url("https://example.com/path/to/") == "https://example.com/path/to"
    
    def test_preserve_query_string(self):
        """Test that query string is preserved."""
        assert normalize_url("https://example.com?key=value") == "https://example.com?key=value"
        assert normalize_url("https://example.com/path?q=1&2=2") == "https://example.com/path?q=1&2=2"
    
    def test_custom_default_scheme(self):
        """Test using custom default scheme."""
        assert normalize_url("example.com", default_scheme='http') == "http://example.com"
        assert normalize_url("example.com", default_scheme='ftp') == "ftp://example.com"
    
    def test_disable_lowercase(self):
        """Test disabling domain lowercasing."""
        assert normalize_url("https://EXAMPLE.COM", lowercase_domain=False) == "https://EXAMPLE.COM"
    
    def test_normalize_invalid_url(self):
        """Test normalizing invalid URLs returns None."""
        assert normalize_url("") is None
        assert normalize_url(None) is None
        assert normalize_url("not-a-url-without-dot") is None
        assert normalize_url("/path/only") is None
    
    def test_complex_url_normalization(self):
        """Test normalization of complex URLs."""
        url = "HTTPS://EXAMPLE.COM:8080/Path/Sub/?q=1#section"
        normalized = normalize_url(url)
        # The trailing slash is removed correctly before the query string
        assert normalized == "https://example.com:8080/Path/Sub?q=1"


class TestGetURLComponents:
    """Tests for get_url_components function."""
    
    def test_extract_components_simple(self):
        """Test extracting components from simple URL."""
        assert get_url_components("https://example.com") == ("https", "example.com", "", "/", "")
        assert get_url_components("http://example.com/path") == ("http", "example.com", "", "/path", "")
    
    def test_extract_components_with_port(self):
        """Test extracting components with port."""
        assert get_url_components("https://example.com:8080") == ("https", "example.com", "8080", "/", "")
        assert get_url_components("http://example.com:443/path") == ("http", "example.com", "443", "/path", "")
    
    def test_extract_components_with_query(self):
        """Test extracting components with query string."""
        assert get_url_components("https://example.com?key=value") == ("https", "example.com", "", "/", "key=value")
    
    def test_extract_components_complex(self):
        """Test extracting components from complex URL."""
        url = "https://sub.example.com:8080/path/to/resource?q=1&2=2#section"
        components = get_url_components(url)
        assert components == ("https", "sub.example.com", "8080", "/path/to/resource", "q=1&2=2")
    
    def test_extract_lowercased(self):
        """Test that scheme and domain are lowercased."""
        assert get_url_components("HTTPS://EXAMPLE.COM") == ("https", "example.com", "", "/", "")
    
    def test_extract_invalid_url(self):
        """Test extracting components from invalid URLs."""
        assert get_url_components("not-a-url") is None
        assert get_url_components("") is None
        assert get_url_components(None) is None


class TestIsURLSafe:
    """Tests for is_url_safe function."""
    
    def test_safe_url(self):
        """Test that safe URLs pass validation."""
        assert is_url_safe("https://example.com") == (True, None)
        assert is_url_safe("https://sub.example.com/path?q=1") == (True, None)
        assert is_url_safe("http://example.com:8080") == (True, None)
    
    def test_unsafe_scheme(self):
        """Test that URLs with disallowed schemes are rejected."""
        result = is_url_safe("ftp://example.com")
        assert result[0] is False
        assert "Invalid URL scheme" in result[1]
    
    def test_unsafe_blocked_domain(self):
        """Test that blocked domains are rejected."""
        result = is_url_safe("https://malicious-site.com")
        assert result[0] is False
        assert "blocked" in result[1].lower()
        assert "malicious-site.com" in result[1]
    
    def test_custom_blocked_domains(self):
        """Test with custom blocked domains list."""
        blocked = {"bad.com", "evil.net"}
        result = is_url_safe("https://bad.com", blocked_domains=blocked)
        assert result[0] is False
        assert "bad.com" in result[1]
        
        result = is_url_safe("https://good.com", blocked_domains=blocked)
        assert result == (True, None)
    
    def test_custom_allowed_schemes(self):
        """Test with custom allowed schemes."""
        result = is_url_safe("https://example.com", allowed_schemes=['http'])
        assert result[0] is False
        assert "Invalid URL scheme" in result[1]
    
    def test_invalid_url(self):
        """Test that invalid URLs are rejected."""
        result = is_url_safe("not-a-url")
        assert result[0] is False
        assert "Invalid URL scheme" in result[1]


class TestDefaultBlockedDomains:
    """Tests for DEFAULT_BLOCKED_DOMAINS constant."""
    
    def test_default_blocked_domains_exists(self):
        """Test that default blocked domains is a set."""
        assert isinstance(DEFAULT_BLOCKED_DOMAINS, set)
        assert len(DEFAULT_BLOCKED_DOMAINS) > 0
    
    def test_default_blocked_domains_content(self):
        """Test that default blocked domains contain expected values."""
        assert "malicious-site.com" in DEFAULT_BLOCKED_DOMAINS
        assert "spam.example" in DEFAULT_BLOCKED_DOMAINS
        assert "phishing.net" in DEFAULT_BLOCKED_DOMAINS


# Specific tests as per acceptance criteria

def test_scheme_validation():
    """Test scheme validation (http/https)."""
    # Test valid schemes
    assert validate_url("https://example.com") is True
    assert validate_url("http://example.com") is True
    assert validate_url("https://sub.example.com/path") is True
    
    # Test invalid schemes
    assert validate_url("ftp://example.com") is False
    assert validate_url("javascript:alert('xss')") is False
    assert validate_url("data:text/plain,hello") is False
    
    # Test missing scheme
    assert validate_url("example.com") is False


def test_domain_blocking():
    """Test blocked domains."""
    # Test default blocked domains
    assert is_domain_blocked("https://malicious-site.com") is True
    assert is_domain_blocked("http://spam.example/path") is True
    assert is_domain_blocked("https://phishing.net") is True
    
    # Test subdomain blocking
    assert is_domain_blocked("https://sub.malicious-site.com") is True
    
    # Test safe domains
    assert is_domain_blocked("https://example.com") is False
    assert is_domain_blocked("https://google.com") is False
    
    # Test custom blocked domains
    custom_blocked = {"bad.com", "evil.net"}
    assert is_domain_blocked("https://bad.com", blocked_domains=custom_blocked) is True
    assert is_domain_blocked("https://good.com", blocked_domains=custom_blocked) is False


def test_url_normalization():
    """Test URL normalization with various input formats."""
    # Test adding default scheme
    assert normalize_url("example.com") == "https://example.com"
    assert normalize_url("example.com/path") == "https://example.com/path"
    
    # Test lowercasing domain
    assert normalize_url("https://EXAMPLE.COM") == "https://example.com"
    assert normalize_url("HTTP://SUB.EXAMPLE.COM") == "http://sub.example.com"
    
    # Test removing trailing slashes
    assert normalize_url("https://example.com/") == "https://example.com"
    assert normalize_url("https://example.com/path/") == "https://example.com/path"
    
    # Test removing fragments
    assert normalize_url("https://example.com#section") == "https://example.com"
    
    # Test preserving ports
    assert normalize_url("https://example.com:8080") == "https://example.com:8080"
    
    # Test complex normalization
    url = "HTTPS://EXAMPLE.COM:8080/PATH/?q=1#section"
    assert normalize_url(url) == "https://example.com:8080/PATH?q=1"
    
    # Test invalid URLs
    assert normalize_url("") is None
    assert normalize_url(None) is None
    assert normalize_url("not-a-valid-url") is None