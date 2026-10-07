"""Single Deny Filter — a logging.Filter for muting one noisy logger.

Exports:
    SingleDenyFilter — Filter that rejects records whose logger name
    contains a configured substring.
"""

from .core import SingleDenyFilter

__all__ = ["SingleDenyFilter"]
