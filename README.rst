=============
configurables
=============


.. image:: https://img.shields.io/pypi/v/configurables.svg
        :target: https://pypi.python.org/pypi/configurables




A quick package to create factories using configuration files of various
syntaxes.


Examples
--------

General use is as follows with the example `ini` file.

.. code-block::

    [PipelineSettings]
    ra=10.0
    dec=20.0
    n_workers=5

.. code-block::

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

    # RA: 10.0, DEC: 20.0
    # Will run with 5 processes
    # Placing output to PosixPath(".")


But in addition you can pass in overrides.

.. code-block::

    print(run_pipeline("config.ini", n_workers=26)

    # RA: 10.0, DEC: 20.0
    # Will run with 26 processes
    # Placing output to PosixPath(".")


You can also pass in overrides via environmental variables.

.. code-block::

    # $ n_workers=3 ./script.py

    print(run_pipeline("config.ini")

    # RA: 10.0, DEC: 20.0
    # Will run with 3 processes
    # Placing output to PosixPath(".")

Currently variables are resolved first by config file, then env variables,
and finally by passed in overrides. But in the future this will be
configurable.


* Free software: MIT license
* Documentation: https://configurables.readthedocs.io.


Features
--------

Typed parameters and options loaded from arbitrary configuration files,
command line parameters, and environmental variables.

Credits
-------

This package was created by William Fong in effort to provide boilerplate
capabilities for overriding configured variables for scientific pipelines.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage