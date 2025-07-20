=====
Usage
=====

Basic Usage
-----------

To use Configurables in a project, you need to:

1. Import the package
2. Define your configuration schema using decorators
3. Load configuration from a file

Here's a simple example:

.. code-block:: python

    import configurables as conf
    
    @conf.configurable("Settings")
    @conf.param("name", type=str)
    @conf.param("value", type=int)
    def process(name, value):
        print(f"{name}: {value}")
    
    # Load from config.ini
    process("config.ini")

Configuration File Format
-------------------------

Configurables supports INI-style configuration files:

.. code-block:: ini

    [Settings]
    name = MyProcess
    value = 42
    
    [Database]
    host = localhost
    port = 5432

Parameters vs Options
---------------------

**Parameters** are required configuration values:

.. code-block:: python

    @conf.param("username", type=str)  # Required

**Options** are optional with default values:

.. code-block:: python

    @conf.option("timeout", type=int, default=30)  # Optional

Type Conversion
---------------

Configurables automatically converts string values to the specified type:

.. code-block:: python

    @conf.param("count", type=int)      # "123" → 123
    @conf.param("rate", type=float)     # "3.14" → 3.14
    @conf.param("debug", type=bool)     # "true" → True
    @conf.param("path", type=pathlib.Path)  # "./data" → Path("./data")

Configuration Sources
---------------------

By default, configuration values are resolved in this order:

1. **Command Line** (highest priority)
2. **Configuration File**
3. **Environment Variables** (lowest priority)

.. code-block:: bash

    # Environment variable
    export alpha=100
    
    # Command line
    python script.py --alpha 200

Custom Resolution Order
-----------------------

You can customize the resolution order:

.. code-block:: python

    from configurables import configurable, ENV, CFG, CLI
    
    @configurable("Settings", order=ENV > CFG > CLI)
    @param("value", type=int)
    def process(value):
        print(value)

Runtime Overrides
-----------------

You can override configuration values at runtime:

.. code-block:: python

    # Override specific values
    process("config.ini", value=999)
    
    # Use a different section
    process("config.ini", _section="Development")

Partial Application
-------------------

Create partially configured functions:

.. code-block:: python

    # Create a partial with fixed configuration
    configured_process = process.partial("config.ini")
    
    # Call multiple times with same config
    configured_process()
    configured_process()

Configuration Generation
------------------------

Generate template configuration files:

.. code-block:: python

    # Generate a template config file
    process.emit("template.ini", alpha=100, beta=0.5)

This creates a configuration file with the provided values and defaults.

Complete Example
----------------

Here's a complete example showing all features:

.. code-block:: python

    import configurables as conf
    import pathlib
    from multiprocessing import cpu_count
    
    @conf.configurable("Pipeline")
    @conf.param("input_file", type=pathlib.Path)
    @conf.param("output_dir", type=pathlib.Path)
    @conf.option("workers", type=int, default=cpu_count())
    @conf.option("verbose", type=bool, default=False)
    def run_pipeline(input_file, output_dir, workers, verbose):
        if verbose:
            print(f"Processing {input_file}")
            print(f"Using {workers} workers")
        
        output_dir.mkdir(exist_ok=True)
        # ... process data ...
        
        return f"Processed to {output_dir}"
    
    # Different ways to use it:
    
    # 1. From config file
    result = run_pipeline("pipeline.ini")
    
    # 2. With overrides
    result = run_pipeline("pipeline.ini", workers=8)
    
    # 3. Direct call with all parameters
    result = run_pipeline(
        input_file=pathlib.Path("data.csv"),
        output_dir=pathlib.Path("output"),
        workers=4,
        verbose=True
    )