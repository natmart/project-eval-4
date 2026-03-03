"""
Tests for the short code generator module
"""
import pytest
from pyshort.generator import (
    generate_random_code,
    generate_custom_code,
    encode_base62,
    decode_base62,
)


class TestGenerateRandomCode:
    """Tests for generate_random_code function"""
    
    def test_default_length(self):
        """Test that default length is 6"""
        code = generate_random_code()
        assert len(code) == 6
    
    def test_custom_length(self):
        """Test custom length parameter"""
        code = generate_random_code(length=10)
        assert len(code) == 10
        
        code = generate_random_code(length=4)
        assert len(code) == 4
    
    def test_alphanumeric_only(self):
        """Test that codes only contain alphanumeric characters"""
        codes = [generate_random_code() for _ in range(100)]
        for code in codes:
            assert code.isalnum()
    
    def test_uniqueness(self):
        """Test that random codes are unique (statistically)"""
        codes = set()
        for _ in range(1000):
            code = generate_random_code()
            codes.add(code)
        # With 6 alphanumeric chars, we have 62^6 possible codes
        # 1000 codes should be unique with very high probability
        assert len(codes) == 1000
    
    def test_invalid_length_zero(self):
        """Test that zero length raises error"""
        with pytest.raises(ValueError, match="length must be at least 1"):
            generate_random_code(length=0)
    
    def test_invalid_length_negative(self):
        """Test that negative length raises error"""
        with pytest.raises(ValueError, match="length must be at least 1"):
            generate_random_code(length=-1)
    
    def test_length_one(self):
        """Test minimum valid length of 1"""
        code = generate_random_code(length=1)
        assert len(code) == 1
        assert code.isalnum()


class TestGenerateCustomCode:
    """Tests for generate_custom_code function"""
    
    def test_valid_simple(self):
        """Test a simple valid custom code"""
        assert generate_custom_code("mycode") == "mycode"
    
    def test_valid_with_numbers(self):
        """Test custom code with numbers"""
        assert generate_custom_code("code123") == "code123"
    
    def test_valid_with_hyphens(self):
        """Test custom code with hyphens"""
        assert generate_custom_code("my-custom-code") == "my-custom-code"
    
    def test_valid_mixed_case(self):
        """Test mixed case is preserved"""
        assert generate_custom_code("MyCode123") == "MyCode123"
    
    def test_whitespace_trimmed(self):
        """Test that leading/trailing whitespace is trimmed"""
        assert generate_custom_code("  mycode  ") == "mycode"
    
    def test_empty_string(self):
        """Test that empty string raises error"""
        with pytest.raises(ValueError, match="custom code cannot be empty"):
            generate_custom_code("")
    
    def test_whitespace_only(self):
        """Test that whitespace-only string raises error"""
        with pytest.raises(ValueError, match="custom code cannot be empty"):
            generate_custom_code("   ")
    
    def test_invalid_characters(self):
        """Test that invalid characters raise error"""
        with pytest.raises(ValueError, match="can only contain alphanumeric"):
            generate_custom_code("my_code")  # underscore not allowed
        
        with pytest.raises(ValueError, match="can only contain alphanumeric"):
            generate_custom_code("my.code")  # dot not allowed
        
        with pytest.raises(ValueError, match="can only contain alphanumeric"):
            generate_custom_code("my code")  # space not allowed
        
        with pytest.raises(ValueError, match="can only contain alphanumeric"):
            generate_custom_code("my@code")  # @ not allowed
    
    def test_starts_with_hyphen(self):
        """Test that code starting with hyphen raises error"""
        with pytest.raises(ValueError, match="cannot start or end with a hyphen"):
            generate_custom_code("-mycode")
    
    def test_ends_with_hyphen(self):
        """Test that code ending with hyphen raises error"""
        with pytest.raises(ValueError, match="cannot start or end with a hyphen"):
            generate_custom_code("mycode-")
    
    def test_consecutive_hyphens(self):
        """Test that consecutive hyphens raise error"""
        with pytest.raises(ValueError, match="cannot contain consecutive hyphens"):
            generate_custom_code("my--code")
    
    def test_single_hyphen(self):
        """Test that single hyphen alone raises error"""
        with pytest.raises(ValueError, match="cannot start or end with a hyphen"):
            generate_custom_code("-")


class TestEncodeBase62:
    """Tests for encode_base62 function"""
    
    def test_zero(self):
        """Test encoding zero"""
        assert encode_base62(0) == "0"
    
    def test_single_digit(self):
        """Test encoding single digits"""
        assert encode_base62(1) == "1"
        assert encode_base62(9) == "9"
    
    def test_lowercase_letters(self):
        """Test encoding 10-35 maps to a-z"""
        assert encode_base62(10) == "a"
        assert encode_base62(11) == "b"
        assert encode_base62(35) == "z"
    
    def test_uppercase_letters(self):
        """Test encoding 36-61 maps to A-Z"""
        assert encode_base62(36) == "A"
        assert encode_base62(37) == "B"
        assert encode_base62(61) == "Z"
    
    def test_base_transitions(self):
        """Test encoding at base boundaries"""
        # 62 should be "10" (1 * 62^1 + 0)
        assert encode_base62(62) == "10"
        
        # 123 should be "1Z" (1 * 62^1 + 61)
        assert encode_base62(123) == "1Z"
        
        # 3844 should be "100" (1 * 62^2 + 0 * 62^1 + 0)
        assert encode_base62(3844) == "100"
    
    def test_deterministic(self):
        """Test that same number always produces same code"""
        for i in [0, 10, 100, 1000, 99999]:
            assert encode_base62(i) == encode_base62(i)
    
    def test_large_number(self):
        """Test encoding a large number"""
        # Just verify it works without error and produces reasonable output
        result = encode_base62(999999999999999999)
        assert isinstance(result, str)
        assert len(result) > 1
    
    def test_negative_number(self):
        """Test that negative numbers raise error"""
        with pytest.raises(ValueError, match="number must be non-negative"):
            encode_base62(-1)


class TestDecodeBase62:
    """Tests for decode_base62 function"""
    
    def test_zero(self):
        """Test decoding zero"""
        assert decode_base62("0") == 0
    
    def test_single_digit(self):
        """Test decoding single digits"""
        assert decode_base62("1") == 1
        assert decode_base62("9") == 9
    
    def test_lowercase_letters(self):
        """Test decoding a-z"""
        assert decode_base62("a") == 10
        assert decode_base62("b") == 11
        assert decode_base62("z") == 35
    
    def test_uppercase_letters(self):
        """Test decoding A-Z"""
        assert decode_base62("A") == 36
        assert decode_b62("B") == 37
        assert decode_base62("Z") == 61
    
    def test_multi_char(self):
        """Test decoding multi-character strings"""
        assert decode_base62("10") == 62  # 1 * 62 + 0
        assert decode_base62("1Z") == 123  # 1 * 62 + 61
        assert decode_base62("100") == 3844  # 1 * 62^2 + 0 + 0
    
    def test_large_string(self):
        """Test decoding a large string"""
        assert decode_base62("zzzz") > 0
    
    def test_empty_string(self):
        """Test that empty string raises error"""
        with pytest.raises(ValueError, match="cannot be empty"):
            decode_base62("")
    
    def test_invalid_characters(self):
        """Test that invalid characters raise error"""
        with pytest.raises(ValueError, match="Invalid base62 character"):
            decode_base62("abc!")
        
        with pytest.raises(ValueError, match="Invalid base62 character"):
            decode_b62("hello world")
    
    def test_roundtrip(self):
        """Test that encode then decode returns original number"""
        test_values = [0, 1, 10, 62, 123, 999, 10000, 999999]
        for value in test_values:
            encoded = encode_base62(value)
            decoded = decode_base62(encoded)
            assert decoded == value


class TestIntegration:
    """Integration tests for the generator module"""
    
    def test_all_functions_importable(self):
        """Test that all main functions can be imported"""
        from pyshort.generator import (
            generate_random_code,
            generate_custom_code,
            encode_base62,
            decode_base62,
        )
        assert callable(generate_random_code)
        assert callable(generate_custom_code)
        assert callable(encode_base62)
        assert callable(decode_base62)
    
    def test_functions_accessible_from_package(self):
        """Test that functions are available from pyshort package"""
        import pyshort
        
        assert hasattr(pyshort, 'generate_random_code')
        assert hasattr(pyshort, 'generate_custom_code')
        assert hasattr(pyshort, 'encode_base62')
        assert hasattr(pyshort, 'decode_base62')
        assert hasattr(pyshort, 'ShortURL')
        assert hasattr(pyshort, 'validate_url')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])