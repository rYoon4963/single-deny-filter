"""Implementation of SingleDenyFilter."""

import logging


class SingleDenyFilter(logging.Filter):
    """A logging filter that rejects records from one named logger subtree.

    ``name`` is matched as a substring of the record's logger name. We
    deliberately use ``in`` rather than a dotted-prefix check: the point of
    this filter is to silence a specific noisy library, and the common case is
    that you know the library's root logger name (e.g. ``"urllib3"``) and want
    every record under it — ``urllib3``, ``urllib3.connection``, and so on —
    gone. A substring match handles that naturally.

    The cost is that ``name="url"`` would also suppress ``my_url_things``.
    That is a real trade-off, but the alternative — a strict hierarchical
    prefix match — is what the standard library's own
    :class:`logging.Filter` *already* does, so there would be no reason for
    this class to exist.

    Attaching to a handler (``handler.addFilter(f)``) drops the records before
    they reach the handler's formatter; attaching to a logger
    (``logger.addFilter(f)``) drops them before they propagate. Either is fine.
    """

    def __init__(self, name: str) -> None:
        # ``logging.Filter.__init__`` accepts a ``name`` argument and performs
        # hierarchical prefix matching on it. That behaviour is NOT what this
        # subclass wants, so we skip the parent initializer entirely and set
        # our own attribute. We must not call super().__init__ here.
        if not isinstance(name, str):
            raise TypeError(
                "SingleDenyFilter requires a str name, got "
                f"{type(name).__name__}"
            )
        if name == "":
            raise ValueError("SingleDenyFilter requires a non-empty name")
        self.name = name

    def filter(self, record: logging.LogRecord) -> bool:
        # Return False to drop the record. The record's logger name is
        # guaranteed by the logging machinery to be a non-None str, so the
        # ``in`` test is safe regardless of what user code named its loggers.
        return self.name not in record.name
