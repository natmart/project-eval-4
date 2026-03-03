"""
pyshort - A simple URL shortener application
"""

__version__ = "0.1.0"

# Import models for easy access
from pyshort.models import ShortURL, validate_url

__all__ = [
    "__version__",
    "ShortURL",
    "validate_url",
]