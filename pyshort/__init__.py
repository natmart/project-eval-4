"""
pyshort - A simple URL shortener application
"""

__version__ = "0.1.0"

# Import models
from pyshort.models import ShortURL, validate_url

# Import validator functions
from pyshort.validator import (
    validate_url as validate_url_full,
    extract_domain,
    is_domain_blocked,
    normalize_url,
    get_url_components,
    is_url_safe,
    DEFAULT_BLOCKED_DOMAINS,
)

# Import generator functions
from pyshort.generator import (
    generate_random_code,
    generate_custom_code,
    encode_base62,
    decode_base62,
)

# Import API components
from pyshort.api import URLShortener
from pyshort.storage import InMemoryStorage
from pyshort.stats import StatsTracker


__all__ = [
    # Version
    "__version__",
    # Models
    "ShortURL",
    "validate_url",
    # Validator functions
    "validate_url_full",
    "extract_domain",
    "is_domain_blocked",
    "normalize_url",
    "get_url_components",
    "is_url_safe",
    "DEFAULT_BLOCKED_DOMAINS",
    # Generator functions
    "generate_random_code",
    "generate_custom_code",
    "encode_base62",
    "decode_base62",
    # API components
    "URLShortener",
    "InMemoryStorage",
    "StatsTracker",
]