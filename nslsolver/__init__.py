"""NSLSolver Python SDK."""

__version__ = "1.1.0"

from .client import NSLSolver
from .exceptions import (
    AuthenticationError,
    BackendError,
    InsufficientBalanceError,
    NSLSolverError,
    RateLimitError,
    SolveError,
    TypeNotAllowedError,
)
from .types import BalanceResult, ChallengeResult, KasadaConfig, KasadaResult, TurnstileResult


def __getattr__(name: str) -> object:
    if name == "AsyncNSLSolver":
        from .async_client import AsyncNSLSolver

        return AsyncNSLSolver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "__version__",
    "NSLSolver",
    "AsyncNSLSolver",
    "TurnstileResult",
    "ChallengeResult",
    "KasadaConfig",
    "KasadaResult",
    "BalanceResult",
    "NSLSolverError",
    "AuthenticationError",
    "InsufficientBalanceError",
    "TypeNotAllowedError",
    "RateLimitError",
    "BackendError",
    "SolveError",
]
