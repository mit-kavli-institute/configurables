=====
Usage
=====
For the following usage, the common example ini file will be used

..code-block:: ini

    [DEFAULT]
    alpha = 1234
    beta = -0.45

    [CUSTOM]
    alpha = -100
    gamma = justsomestr


To use Configurables in a project

.. code-block:: python
    :linenos:

    from configurables import configure, define_param, define_option

    @configure()
    @define_param("alpha", type=int)
    @define_param("beta", type=float)
    @define_option("gamma", default="somestr")
    def to_configure(alpha, beta, gamma):
        print(f"Alpha: {alpha} Beta: {beta} Gamma {gamma}")

    to_configure("./example.ini")

    # Alpha: 1234 Beta: -0.45 Gamma somestr
