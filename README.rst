=============
Configurables
=============


.. image:: https://img.shields.io/pypi/v/configurables.svg
        :target: https://pypi.python.org/pypi/configurables

.. image:: https://img.shields.io/travis/WilliamCFong/configurables.svg
        :target: https://travis-ci.com/WilliamCFong/configurables

.. image:: https://readthedocs.org/projects/configurables/badge/?version=latest
        :target: https://configurables.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




A quick package to create factories using configuration files of various syntaxes.


Examples
-----
.. code-block:: python
    :linenos:

    import configurables as conf
    import pathlib

    from multiprocessing import cpu_count


    @conf.configurable("PipelineSettings")
    @conf.define_param("ra", type=float)
    @conf.define_param("dec", type=float)
    @conf.define_option("n_workers", type=int, default=cpu_count())
    @conf.define_option("output_path", type=pathlib.Path, default="./")
    def run_pipeline(ra, dec, n_workers, output_path):
        return (
            f"RA: {ra}, DEC: {dec}\n"
            f"Will run with {n_workers} processes\n"
            f"Placing output to {output_path}"
        )

    print(run_pipeline("config.ini"))


* Free software: MIT license
* Documentation: https://configurables.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
