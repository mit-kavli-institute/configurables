#!/usr/bin/env python
"""
Demonstration of improved typing in configurables.

This script shows how the enhanced type system makes it clear that
configuration files are valid inputs to decorated functions.
"""
from pathlib import Path
from typing import List

import configurables as conf


# Example 1: Simple typed function
@conf.configurable("Database")
@conf.param("host", type=str)
@conf.param("port", type=int)
@conf.option("timeout", type=int, default=30)
def connect_to_database(host: str, port: int, timeout: int = 30) -> str:
    """Connect to a database with typed parameters."""
    return f"Connected to {host}:{port} with timeout={timeout}s"


# Example 2: Function with complex types
@conf.configurable("Pipeline")
@conf.param("input_files", type=lambda s: s.split(','))
@conf.param("output_dir", type=Path)
@conf.option("parallel", type=bool, default=True)
def process_files(
    input_files: List[str], 
    output_dir: Path, 
    parallel: bool = True
) -> dict:
    """Process multiple files with complex types."""
    return {
        "files": input_files,
        "output": str(output_dir),
        "mode": "parallel" if parallel else "sequential"
    }


def main():
    """Demonstrate the typing improvements."""
    
    # Create example configuration files
    with open("db_config.ini", "w") as f:
        f.write("[Database]\n")
        f.write("host = localhost\n")
        f.write("port = 5432\n")
    
    with open("pipeline_config.ini", "w") as f:
        f.write("[Pipeline]\n")
        f.write("input_files = file1.txt,file2.txt,file3.txt\n")
        f.write("output_dir = /tmp/output\n")
    
    try:
        print("=== ConfigurationFactory Type Demo ===\n")
        
        # 1. Call with config file - IDE should show this is valid
        print("1. Call with config file:")
        result1 = connect_to_database("db_config.ini")
        print(f"   Result: {result1}")
        print(f"   Return type: {type(result1).__name__}")
        
        # 2. Call with config file and overrides
        print("\n2. Call with config file and overrides:")
        result2 = connect_to_database("db_config.ini", timeout=60)
        print(f"   Result: {result2}")
        
        # 3. Direct call with all parameters
        print("\n3. Direct call with all parameters:")
        result3 = connect_to_database(host="remote", port=3306, timeout=45)
        print(f"   Result: {result3}")
        
        # 4. Complex types example
        print("\n4. Complex types example:")
        result4 = process_files("pipeline_config.ini")
        print(f"   Result: {result4}")
        print(f"   Return type: {type(result4).__name__}")
        
        # 5. Partial function
        print("\n5. Partial function with config:")
        db_func = connect_to_database.partial("db_config.ini")
        result5 = db_func()
        print(f"   Result: {result5}")
        
        # The key improvement is that IDEs and type checkers now understand:
        # - connect_to_database can be called with just a config file path
        # - The return type is preserved (str)
        # - Overrides are properly typed
        # - Both calling styles are valid
        
        print("\n✓ All examples demonstrate improved typing!")
        
    finally:
        # Cleanup
        Path("db_config.ini").unlink(missing_ok=True)
        Path("pipeline_config.ini").unlink(missing_ok=True)


if __name__ == "__main__":
    main()