"""
Basic tests to validate the test environment setup.
"""

def test_basic_math():
    """Test that basic math works - should always pass."""
    assert 1 + 1 == 2

def test_imports():
    """Test that we can import our modules."""
    import todo_tracker
    import todo_tracker.scanner
    import todo_tracker.github_client
    import todo_tracker.cli
    assert True

def test_python_version():
    """Test that we're using a supported Python version."""
    import sys
    assert sys.version_info >= (3, 9)
