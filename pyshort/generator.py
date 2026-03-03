"""
Short code generation functions for the pyshort URL shortener
"""
import random
import string
from typing import Optional


def generate_random_code(length: int = 6) -> str:
    """
    Generate a random short code.
    
    The code is generated using a random selection from alphanumeric characters
    (0-9, a-z, A-Z). Each call produces a unique, random code.
    
    Args:
        length: The length of the generated code (default: 6)
        
    Returns:
        A random alphanumeric string of the specified length
        
    Examples:
        >>> code = generate_random_code()
        >>> len(code)
        6
        >>> code = generate_random_code(length=8)
        >>> len(code)
        8
    """
    if length < 1:
        raise ValueError("length must be at least 1")
    
    characters = string.ascii_letters + string.digits  # 0-9, a-z, A-Z
    return ''.join(random.choices(characters, k=length))


def generate_custom_code(custom_code: str) -> str:
    """
    Validate and return a custom short code provided by the user.
    
    This function accepts a user-provided custom code and validates it.
    The code must not be empty and should only contain alphanumeric characters
    and hyphens.
    
    Args:
        custom_code: The custom code provided by the user
        
    Returns:
        The validated custom code
        
    Raises:
        ValueError: If the custom_code is empty or contains invalid characters
        
    Examples:
        >>> generate_custom_code("my-custom-link")
        'my-custom-link'
        >>> generate_custom_code("abc123")
        'abc123'
    """
    if not custom_code or not custom_code.strip():
        raise ValueError("custom code cannot be empty")
    
    # Strip whitespace
    custom_code = custom_code.strip()
    
    # Validate characters: only alphanumeric and hyphens allowed
    valid_chars = set(string.ascii_letters + string.digits + '-')
    if not all(c in valid_chars for c in custom_code):
        raise ValueError(
            "custom code can only contain alphanumeric characters and hyphens"
        )
    
    # Code should not start or end with hyphen
    if custom_code.startswith('-') or custom_code.endswith('-'):
        raise ValueError(
            "custom code cannot start or end with a hyphen"
        )
    
    # No consecutive hyphens
    if '--' in custom_code:
        raise ValueError(
            "custom code cannot contain consecutive hyphens"
        )
    
    return custom_code


def encode_base62(number: int) -> str:
    """
    Encode a number to a base62 string.
    
    Base62 encoding uses the characters 0-9, a-z, A-Z (in that order) to
    represent numbers. This is deterministic - the same number always
    produces the same encoded string.
    
    Characters are ordered as: 0-9 (0-9), a-z (10-35), A-Z (36-61)
    
    Args:
        number: The non-negative integer to encode
        
    Returns:
        The base62 encoded string representation of the number
        
    Raises:
        ValueError: If number is negative
        
    Examples:
        >>> encode_base62(0)
        '0'
        >>> encode_base62(10)
        'a'
        >>> encode_base62(61)
        'Z'
        >>> encode_base62(12345)
        'd7C'
    """
    if number < 0:
        raise ValueError("number must be non-negative")
    
    # Base62 character set
    characters = string.digits + string.ascii_letters + string.ascii_uppercase[:0]
    # Fix: ensure we have proper base62 charset: 0-9, a-z, A-Z
    characters = string.digits + string.ascii_lowercase + string.ascii_uppercase
    
    if number == 0:
        return characters[0]
    
    encoding = []
    base = len(characters)  # 62
    
    while number > 0:
        number, remainder = divmod(number, base)
        encoding.append(characters[remainder])
    
    # Reverse since we built it backwards
    return ''.join(reversed(encoding))[::-1]  # Reverse to get correct order


def encode_base62_fixed(number: int) -> str:
    """
    Encode a number to a base62 string (fixed implementation).
    
    Base62 encoding uses the characters 0-9, a-z, A-Z (in that order) to
    represent numbers. This is deterministic - the same number always
    produces the same encoded string.
    
    Characters are ordered as: 0-9 (0-9), a-z (10-35), A-Z (36-61)
    
    Args:
        number: The non-negative integer to encode
        
    Returns:
        The base62 encoded string representation of the number
        
    Raises:
        ValueError: If number is negative
        
    Examples:
        >>> encode_base62_fixed(0)
        '0'
        >>> encode_base62_fixed(10)
        'a'
        >>> encode_base62_fixed(61)
        'Z'
        >>> encode_base62_fixed(62)
        '10'
    """
    if number < 0:
        raise ValueError("number must be non-negative")
    
    # Base62 character set: 0-9, a-z, A-Z
    characters = string.digits + string.ascii_lowercase + string.ascii_uppercase
    
    if number == 0:
        return characters[0]
    
    encoding = []
    base = 62
    
    while number > 0:
        number, remainder = divmod(number, base)
        encoding.append(characters[remainder])
    
    # Reverse to get the correct order
    return ''.join(reversed(encoding))


def decode_base62(encoded: str) -> int:
    """
    Decode a base62 string back to a number.
    
    Args:
        encoded: The base62 encoded string to decode
        
    Returns:
        The decoded integer
        
    Raises:
        ValueError: If the string contains invalid base62 characters
        
    Examples:
        >>> decode_base62('0')
        0
        >>> decode_base62('a')
        10
        >>> decode_base62('Z')
        61
    """
    if not encoded:
        raise ValueError("encoded string cannot be empty")
    
    characters = string.digits + string.ascii_lowercase + string.ascii_uppercase
    char_map = {c: i for i, c in enumerate(characters)}
    
    result = 0
    base = 62
    
    for char in encoded:
        if char not in char_map:
            raise ValueError(f"Invalid base62 character: {char}")
        result = result * base + char_map[char]
    
    return result


# Use the fixed version as the primary function
encode_base62 = encode_base62_fixed