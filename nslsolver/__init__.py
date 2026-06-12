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
from .types import (
    AkamaiResult,
    BalanceResult,
    ChallengeResult,
    KasadaConfig,
    KasadaResult,
    RecaptchaV3Result,
    TurnstileResult,
)


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
    "AkamaiResult",
    "RecaptchaV3Result",
    "BalanceResult",
    "NSLSolverError",
    "AuthenticationError",
    "InsufficientBalanceError",
    "TypeNotAllowedError",
    "RateLimitError",
    "BackendError",
    "SolveError",
]
