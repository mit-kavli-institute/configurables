class InvalidOrdering(Exception):
    """
    Raised when the given set of ordering pairs results in something
    impossible to resolve.

    Example
    -------
    ENV > ENV
    ENV > CFG > ENV

    etc.
    """

    pass


class ResolutionDefinition:
    """
    This class handles the definitions of resolution orderings. Its most
    dynamic behavior is overriding ``>`` and ``<`` operators. This allows
    developers to augment resolution orderings.

    Example
    -------
    >>> import configurables as conf
    >>>
    >>> @conf.configurables("Test", ordering=conf.ENV > conf.CFG)
    >>> @conf.param("key", type=str)
    >>> def load(key):
    >>>     print(key)

    This particular example would have ``configurables`` use values found
    in ENV (environmental variables) *above* values found in configuration
    files.

    Notes
    -----
    By default orderings are as follows CLI > CFG > ENV.
    """

    def __init__(self, first_element):
        self.interpreter_order = [first_element]

    def __lt__(self, rhs):
        if rhs in self.interpreter_order:
            raise InvalidOrdering()

        self.interpreter_order.insert(0, rhs)
        return self

    def __gt__(self, rhs):
        if rhs in self.interpreter_order:
            raise InvalidOrdering()

        self.interpreter_order.append(rhs)
        return self

    def __repr__(self):
        return " > ".join(map(str, self.interpreter_order))

    def load(self, **context):
        payload = {}

        for interpreter in self.interpreter_order:
            kwargs = interpreter.load(**context)
            payload.update(kwargs)

        return payload
