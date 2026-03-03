"""
pyshort - A simple URL shortener application

This package provides utilities for shortening URLs, generating short codes,
validating URLs, and handling URL metadata.

Example usage:
    >>> from pyshort import generate_random_code, validate_url, ShortURL
    >>> code = generate_random_code(length=6)
    >>> is_valid = validate_url('https://example.com')
"""

__version__ = "0.1.0"

# Main public API exports
from pyshort.models import ShortURL, validate_url
from pyshort.generator import (
    generate_random_code,
    generate_custom_code,
    encode_base62,
    decode_base62,
)
from pyshort.validator import (
    validate_url as validate_url_full,
    extract_domain,
    is_domain_blocked,
    normalize_url,
    get_url_components,
    is_url_safe,
    DEFAULT_BLOCKED_DOMAINS,
)

__all__ = [
    # Version information
    "__version__",

    # Main models (primary public API)
    "ShortURL",
    "validate_url",

    # Short code generation
    "generate_random_code",
    "generate_custom_code",
    "encode_base62",
    "decode_base62",

    # URL validation and normalization
    "validate_url_full",
    "extract_domain",
    "is_domain_blocked",
    "normalize_url",
    "get_url_components",
    "is_url_safe",
    "DEFAULT_BLOCKED_DOMAINS",
]