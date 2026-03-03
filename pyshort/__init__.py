"""
pyshort - A simple URL shortener application
"""

__version__ = "0.1.0"

# Import models
from pyshort.models import ShortURL, validate_url

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
    # Models
    "ShortURL",
    "validate_url",
    # Generator functions
    "generate_random_code",
    "generate_custom_code",
    "encode_base62",
    "decode_base62",
]