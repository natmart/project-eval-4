"""
pyshort - A simple URL shortener application
"""

__version__ = "0.1.0"

# Import API
from pyshort.api import URLShortener

# Import storage
from pyshort.storage import InMemoryStorage

# Import stats
from pyshort.stats import StatsTracker

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

__all__ = [
    # Version
    "__version__",
    # Main API
    "URLShortener",
    # Storage
    "InMemoryStorage",
    # Stats
    "StatsTracker",
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
]