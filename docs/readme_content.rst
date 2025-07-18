=============
Configurables
=============

.. image:: https://img.shields.io/pypi/v/configurables.svg
        :target: https://pypi.python.org/pypi/configurables


**Configurables** is a Python package that provides a decorator-based system for managing 
configuration from multiple sources (configuration files, environment variables, and 
command-line arguments). It's designed for scientific computing pipelines where parameters 
need to be loaded from various sources with proper type conversion and validation.

* Free software: MIT license
* Documentation: https://configurables.readthedocs.io


Features
--------

* **Multiple Configuration Sources**: Load configuration from INI files, environment variables, and command-line arguments
* **Type Safety**: Automatic type conversion with validation  
* **Decorator-based API**: Clean, intuitive interface using Python decorators
* **Flexible Resolution Order**: Configurable precedence for configuration sources (default: CLI > CFG > ENV)
* **Default Values**: Support for optional parameters with defaults
* **Configuration Generation**: Automatically generate configuration file templates


Quick Start
-----------

Install the package:

.. code-block:: bash

    pip install configurables

Create a configurable function:

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


Examples
--------

Basic Usage with INI File
~~~~~~~~~~~~~~~~~~~~~~~~~

Create a configuration file ``config.ini``:

.. code-block:: ini

    [PipelineSettings]
    ra=10.0
    dec=20.0
    n_workers=5

Use it in your code:

.. code-block:: python

    import configurables as conf
    import pathlib
    from multiprocessing import cpu_count

    @conf.configurable("PipelineSettings")
    @conf.param("ra", type=float)
    @conf.param("dec", type=float)
    @conf.option("n_workers", type=int, default=cpu_count())
    @conf.option("output_path", type=pathlib.Path, default="./")
    def run_pipeline(ra, dec, n_workers, output_path):
        return (
            f"RA: {ra}, DEC: {dec}\n"
            f"Will run with {n_workers} processes\n"
            f"Placing output to {output_path}"
        )

    print(run_pipeline("config.ini"))

    # Output:
    # RA: 10.0, DEC: 20.0
    # Will run with 5 processes
    # Placing output to PosixPath(".")


Runtime Overrides
~~~~~~~~~~~~~~~~~

You can override configuration values at runtime:

.. code-block:: python

    # Override specific values
    print(run_pipeline("config.ini", n_workers=26))

    # Output:
    # RA: 10.0, DEC: 20.0
    # Will run with 26 processes
    # Placing output to PosixPath(".")


Configuration Sources Priority
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, configuration values are resolved in this order (highest to lowest priority):

1. **Command-line arguments** (``--key value``)
2. **Configuration files** (``.ini``, ``.conf``)
3. **Environment variables**

.. code-block:: bash

    # Set environment variable
    export n_workers=3
    
    # Command line overrides everything
    python script.py --n_workers 10

You can customize the resolution order:

.. code-block:: python

    from configurables import ENV, CFG, CLI
    
    @conf.configurable("Settings", order=ENV > CFG > CLI)
    @conf.param("api_key", type=str)
    def connect(api_key):
        # Now environment variables have highest priority
        return f"Connected with key: {api_key}"


Generate Configuration Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Automatically generate template configuration files:

.. code-block:: python

    # Generate a template with defaults and example values
    run_pipeline.emit("template.ini", ra=15.5, dec=30.0)

This creates a configuration file with the provided values that users can customize.


Credits
-------

This package was created by William Christopher Fong to provide boilerplate
capabilities for overriding configured variables for scientific pipelines.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage