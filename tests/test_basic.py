"""
Basic tests to verify project setup
"""

def test_import():
    """Test that we can import the pyshort package"""
    import pyshort
    assert pyshort.__version__ == "0.1.0"


def test_simple_math():
    """A simple test to verify pytest is working"""
    assert 1 + 1 == 2