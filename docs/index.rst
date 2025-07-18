Welcome to Configurables documentation!
=======================================

**Configurables** is a Python package that provides a decorator-based system for managing 
configuration from multiple sources (configuration files, environment variables, and 
command-line arguments). It's designed for scientific computing pipelines where parameters 
need to be loaded from various sources with proper type conversion and validation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   installation
   usage
   api
   contributing
   authors
   history

Key Features
------------

* **Multiple Configuration Sources**: Load configuration from INI files, environment variables, and command-line arguments
* **Type Safety**: Automatic type conversion with validation
* **Decorator-based API**: Clean, intuitive interface using Python decorators
* **Flexible Resolution Order**: Configurable precedence for configuration sources (default: CLI > CFG > ENV)
* **Default Values**: Support for optional parameters with defaults
* **Configuration Generation**: Automatically generate configuration file templates

Quick Example
-------------

.. code-block:: python

    import configurables as conf
    from pathlib import Path

    @conf.configurable("Settings")
    @conf.param("input_file", type=Path)
    @conf.param("iterations", type=int)
    @conf.option("debug", type=bool, default=False)
    def process_data(input_file, iterations, debug):
        print(f"Processing {input_file} for {iterations} iterations")
        if debug:
            print("Debug mode enabled")
        
    # Load from config.ini
    process_data("config.ini")
    
    # Override with command-line arguments
    # python script.py --iterations 100

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`