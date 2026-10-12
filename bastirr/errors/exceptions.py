"""Bastirr-specific exceptions."""


class ContextOverflowError(RuntimeError):
    """Raised when a model request exceeds the provider context window.

    Screening runners treat this as a hard failure: stop resume attempts and
    mark the run incomplete/error with ``error_type=context_overflow``.
    """
