"""NSLSolver SDK exceptions."""

from typing import Optional


class NSLSolverError(Exception):
    """Base exception for all NSLSolver API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[dict] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code!r})"
        )


class AuthenticationError(NSLSolverError):
    """Invalid or missing API key (401)."""


class InsufficientBalanceError(NSLSolverError):
    """Account balance too low (402)."""


class TypeNotAllowedError(NSLSolverError):
    """Solve type not allowed for this key (403)."""


class RateLimitError(NSLSolverError):
    """Rate limit exceeded (429). Retried automatically."""


class BackendError(NSLSolverError):
    """Backend unavailable (503). Retried automatically."""


class SolveError(NSLSolverError):
    """Solve request failed (400)."""
