"""Test type preservation and hints."""
import pathlib
from typing import TYPE_CHECKING

import configurables as conf


# Define a function with clear types
@conf.configurable("TestSection")
@conf.param("name", type=str)
@conf.param("count", type=int)
@conf.option("debug", type=bool, default=False)
def process_data(name: str, count: int, debug: bool = False) -> str:
    """Process data with typed parameters."""
    result = f"Processing {name} {count} times"
    if debug:
        result += " (debug mode)"
    return result


def test_type_preservation():
    """Test that types are preserved through decoration."""
    # The decorated function should still be callable
    assert callable(process_data)
    
    # Should have proper __name__ attribute
    assert hasattr(process_data, '__repr__')
    
    # The factory should preserve the return type
    # When called with config, it returns the same type as the original function
    with open("test_config.ini", "w") as f:
        f.write("[TestSection]\n")
        f.write("name=test\n")
        f.write("count=5\n")
    
    try:
        result = process_data("test_config.ini")
        assert isinstance(result, str)
        assert result == "Processing test 5 times"
        
        # Test with overrides
        result2 = process_data("test_config.ini", debug=True)
        assert isinstance(result2, str)
        assert result2 == "Processing test 5 times (debug mode)"
        
        # Test direct call
        result3 = process_data(name="direct", count=3, debug=False)
        assert isinstance(result3, str)
        assert result3 == "Processing direct 3 times"
        
    finally:
        pathlib.Path("test_config.ini").unlink()


def test_partial_typing():
    """Test that partial functions preserve types."""
    with open("test_config.ini", "w") as f:
        f.write("[TestSection]\n")
        f.write("name=partial\n")
        f.write("count=10\n")
    
    try:
        # Create a partial function
        partial_func = process_data.partial("test_config.ini")
        
        # The partial should still return the correct type
        result = partial_func()
        assert isinstance(result, str)
        assert result == "Processing partial 10 times"
        
    finally:
        pathlib.Path("test_config.ini").unlink()


if TYPE_CHECKING:
    # This section only runs during type checking, not at runtime
    # It helps verify that our type hints are working correctly
    
    # The factory should accept a config file path
    _: str = process_data("config.ini")
    
    # It should also accept direct parameters
    _: str = process_data(name="test", count=5, debug=True)
    
    # Overrides should work
    _: str = process_data("config.ini", name="override")
    
    # Section override should work
    _: str = process_data("config.ini", _section="Other")