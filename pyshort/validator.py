"""
URL validation and normalization module for pyshort.

This module provides functions to validate URL schemes, extract and validate domains,
check against blocked domains, and normalize URLs.
"""

from typing import List, Optional, Tuple, Set
from urllib.parse import urlparse, urlunparse


# Default list of blocked domains
DEFAULT_BLOCKED_DOMAINS: Set[str] = {
    "malicious-site.com",
    "spam.example",
    "phishing.net",
}


def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
    """
    Validate a URL string.
    
    Checks if the URL has a valid scheme (default: http, https) and a valid domain.
    
    Args:
        url: The URL string to validate
        allowed_schemes: List of allowed schemes (default: ['http', 'https'])
        
    Returns:
        True if the URL is valid, False otherwise
        
    Examples:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("ftp://example.com")
        False
        >>> validate_url("not-a-url")
        False
        >>> validate_url("https://example.com", allowed_schemes=['http'])
        False
    """
    if not url or not isinstance(url, str):
        return False
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    try:
        parsed = urlparse(url)
        
        # Check if scheme is present and allowed
        if not parsed.scheme or parsed.scheme.lower() not in allowed_schemes:
            return False
        
        # Check if domain (netloc) is present
        if not parsed.netloc:
            return False
        
        # Validate basic domain format
        domain = parsed.netloc
        
        # Remove port if present
        domain = domain.split(':')[0]
        
        # Basic domain validation - should have at least one dot and valid characters
        if not domain or '.' not in domain:
            return False
        
        # Check for invalid characters in domain
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-')
        if not all(c in valid_chars for c in domain):
            return False
        
        # Domain should not start or end with dot or hyphen
        if domain.startswith('.') or domain.endswith('.'):
            return False
        if domain.startswith('-') or domain.endswith('-'):
            return False
        
        return True
        
    except Exception:
        return False


def extract_domain(url: str) -> Optional[str]:
    """
    Extract the domain from a URL string.
    
    Args:
        url: The URL string to extract domain from
        
    Returns:
        The domain name (lowercase, without port) or None if invalid
        
    Examples:
        >>> extract_domain("https://example.com/path")
        'example.com'
        >>> extract_domain("http://sub.example.com:8080/path")
        'sub.example.com'
        >>> extract_domain("invalid-url")
        None
    """
    if not url or not isinstance(url, str):
        return None
    
    try:
        parsed = urlparse(url)
        
        if not parsed.netloc:
            return None
        
        # Remove port and convert to lowercase
        domain = parsed.netloc.split(':')[0].lower()
        
        return domain
        
    except Exception:
        return None


def is_domain_blocked(
    url: str,
    blocked_domains: Optional[Set[str]] = None,
    case_sensitive: bool = False
) -> bool:
    """
    Check if a URL's domain is in the blocked domains list.
    
    Args:
        url: The URL to check
        blocked_domains: Set of blocked domains (default: DEFAULT_BLOCKED_DOMAINS)
        case_sensitive: Whether domain matching is case sensitive (default: False)
        
    Returns:
        True if the domain is blocked, False otherwise
        
    Examples:
        >>> is_domain_blocked("https://malicious-site.com/path")
        True
        >>> is_domain_blocked("https://good-site.com/path")
        False
        >>> is_domain_blocked("https://MALICIOUS-SITE.COM")  # case insensitive by default
        True
    """
    if blocked_domains is None:
        blocked_domains = DEFAULT_BLOCKED_DOMAINS
    
    domain = extract_domain(url)
    
    if not domain:
        return False
    
    # Normalize case for comparison if not case sensitive
    if not case_sensitive:
        domain = domain.lower()
        blocked_domains = {d.lower() for d in blocked_domains}
    
    # Check exact match
    if domain in blocked_domains:
        return True
    
    # Check subdomains - e.g., if "bad.com" is blocked, "sub.bad.com" should also be blocked
    for blocked in blocked_domains:
        if blocked and domain.endswith('.' + blocked):
            return True
    
    return False


def normalize_url(
    url: str,
    default_scheme: str = 'https',
    lowercase_domain: bool = True
) -> Optional[str]:
    """
    Normalize a URL string.
    
    Normalization includes:
    - Adding default scheme if missing
    - Converting domain to lowercase
    - Removing fragments
    - Removing trailing slash from path (unless root)
    
    Args:
        url: The URL string to normalize
        default_scheme: The scheme to add if missing (default: 'https')
        lowercase_domain: Whether to convert domain to lowercase (default: True)
        
    Returns:
        The normalized URL string, or None if invalid
        
    Examples:
        >>> normalize_url("example.com")
        'https://example.com'
        >>> normalize_url("HTTP://EXAMPLE.COM/path")
        'http://example.com/path'
        >>> normalize_url("https://example.com/#section")
        'https://example.com'
        >>> normalize_url("https://example.com/path/")
        'https://example.com/path'
    """
    if not url or not isinstance(url, str):
        return None
    
    url = url.strip()
    
    if not url:
        return None
    
    try:
        # If no scheme is present, add the default scheme
        if '://' not in url:
            # Check if it looks like a URL (has domain-like structure)
            if '.' in url and not url.startswith('/'):
                url = f"{default_scheme}://{url}"
            else:
                return None
        
        parsed = urlparse(url)
        
        # Validate basic components
        if not parsed.netloc:
            return None
        
        # Get components
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc
        
        # Lowercase the domain if requested
        if lowercase_domain:
            # Split on ':' to separate port
            domain_parts = netloc.split(':')
            domain_parts[0] = domain_parts[0].lower()
            netloc = ':'.join(domain_parts)
        
        # Get path and normalize (remove trailing slash unless it's the only path)
        path = parsed.path
        if path and path != '/' and path.endswith('/'):
            path = path.rstrip('/')
        
        # Reconstruct URL without fragment
        normalized = urlunparse((
            scheme,
            netloc,
            path,
            parsed.params,  # Keep parameters
            parsed.query,  # Keep query string
            ''  # Remove fragment
        ))
        
        return normalized
        
    except Exception:
        return None


def get_url_components(url: str) -> Optional[Tuple[str, str, str, str, str]]:
    """
    Extract and return individual URL components.
    
    Args:
        url: The URL string to parse
        
    Returns:
        Tuple of (scheme, domain, port, path, query) or None if invalid
        
    Examples:
        >>> get_url_components("https://example.com:8080/path?query=value")
        ('https', 'example.com', '8080', '/path', 'query=value')
    """
    if not url or not isinstance(url, str):
        return None
    
    try:
        parsed = urlparse(url)
        
        if not parsed.netloc:
            return None
        
        # Extract domain and port
        netloc_parts = parsed.netloc.split(':')
        domain = netloc_parts[0].lower()
        port = netloc_parts[1] if len(netloc_parts) > 1 else ''
        
        return (
            parsed.scheme.lower(),
            domain,
            port,
            parsed.path or '/',
            parsed.query
        )
        
    except Exception:
        return None


def is_url_safe(
    url: str,
    blocked_domains: Optional[Set[str]] = None,
    allowed_schemes: Optional[List[str]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive URL safety check.
    
    Checks if a URL is valid and safe by validating:
    - URL structure and scheme
    - Domain not in blocked list
    
    Args:
        url: The URL to check
        blocked_domains: Set of blocked domains
        allowed_schemes: List of allowed schemes (default: ['http', 'https'])
        
    Returns:
        Tuple of (is_safe, error_message). If is_safe is True, error_message is None.
        
    Examples:
        >>> is_url_safe("https://example.com")
        (True, None)
        >>> is_url_safe("https://malicious-site.com")
        (False, 'Domain is blocked: malicious-site.com')
        >>> is_url_safe("ftp://example.com")
        (False, 'Invalid URL scheme')
    """
    # Validate URL structure and scheme
    if not validate_url(url, allowed_schemes=allowed_schemes):
        return (False, 'Invalid URL scheme or format')
    
    # Check if domain is blocked
    domain = extract_domain(url)
    if domain and is_domain_blocked(url, blocked_domains=blocked_domains):
        return (False, f'Domain is blocked: {domain}')
    
    return (True, None)