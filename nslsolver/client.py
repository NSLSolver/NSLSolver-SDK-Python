"""Synchronous NSLSolver client."""

import time
import logging
from typing import Any, Dict, Optional

import requests

from .exceptions import (
    AuthenticationError,
    BackendError,
    InsufficientBalanceError,
    NSLSolverError,
    RateLimitError,
    SolveError,
    TypeNotAllowedError,
)
from .types import BalanceResult, ChallengeResult, TurnstileResult

logger = logging.getLogger("nslsolver")

_DEFAULT_BASE_URL = "https://api.nslsolver.com"
_DEFAULT_TIMEOUT = 120
_DEFAULT_MAX_RETRIES = 3
_INITIAL_BACKOFF = 1.0
_BACKOFF_MULTIPLIER = 2.0
_MAX_BACKOFF = 30.0

# Errors worth retrying
_RETRYABLE_EXCEPTIONS = (RateLimitError, BackendError)


class NSLSolver:
    """Synchronous client for the NSLSolver API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must be a non-empty string.")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-API-Key": self._api_key,
                "Content-Type": "application/json",
                "User-Agent": "nslsolver-python/1.0.0",
            }
        )

    # -- Public API ----------------------------------------------------------

    def solve_turnstile(
        self,
        site_key: str,
        url: str,
        action: Optional[str] = None,
        cdata: Optional[str] = None,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TurnstileResult:
        """Solve a Cloudflare Turnstile captcha."""
        payload: Dict[str, Any] = {
            "type": "turnstile",
            "site_key": site_key,
            "url": url,
        }
        if action is not None:
            payload["action"] = action
        if cdata is not None:
            payload["cdata"] = cdata
        if proxy is not None:
            payload["proxy"] = proxy
        if user_agent is not None:
            payload["user_agent"] = user_agent

        data = self._request("POST", "/solve", json_body=payload)

        return TurnstileResult(
            token=data["token"],
            type=data.get("type", "turnstile"),
        )

    def solve_challenge(
        self,
        url: str,
        proxy: str,
        user_agent: Optional[str] = None,
    ) -> ChallengeResult:
        """Solve a Cloudflare challenge page."""
        payload: Dict[str, Any] = {
            "type": "challenge",
            "url": url,
            "proxy": proxy,
        }
        if user_agent is not None:
            payload["user_agent"] = user_agent

        data = self._request("POST", "/solve", json_body=payload)

        return ChallengeResult(
            cookies=data.get("cookies", {}),
            user_agent=data.get("user_agent", ""),
            type=data.get("type", "challenge"),
        )

    def get_balance(self) -> BalanceResult:
        """Retrieve current account balance."""
        data = self._request("GET", "/balance")

        known_keys = {"balance", "max_threads", "allowed_types"}
        extra = {k: v for k, v in data.items() if k not in known_keys}

        return BalanceResult(
            balance=float(data["balance"]),
            max_threads=int(data["max_threads"]),
            allowed_types=list(data.get("allowed_types", [])),
            extra=extra,
        )

    # -- Internal ------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute an HTTP request with retries on transient errors."""
        url = f"{self._base_url}{path}"
        last_exc: Optional[Exception] = None
        backoff = _INITIAL_BACKOFF

        for attempt in range(self._max_retries + 1):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    json=json_body,
                    timeout=self._timeout,
                )

                if response.status_code == 200:
                    return response.json()  # type: ignore[no-any-return]

                self._handle_error_response(response)

            except _RETRYABLE_EXCEPTIONS as exc:
                last_exc = exc
            except requests.exceptions.Timeout:
                last_exc = NSLSolverError(f"Request timed out after {self._timeout}s.")
            except requests.exceptions.ConnectionError:
                last_exc = NSLSolverError("Connection error.")
            else:
                # _handle_error_response always raises, so we only land here
                # on a 200, which already returned above.
                break  # pragma: no cover

            # Retry or give up
            if attempt < self._max_retries:
                sleep_time = min(backoff, _MAX_BACKOFF)
                logger.warning(
                    "%s on attempt %d/%d, retrying in %.1fs",
                    last_exc,
                    attempt + 1,
                    self._max_retries + 1,
                    sleep_time,
                )
                time.sleep(sleep_time)
                backoff *= _BACKOFF_MULTIPLIER
            else:
                raise last_exc  # type: ignore[misc]

        # Should not be reached, but keeps the type checker happy.
        if last_exc is not None:
            raise last_exc
        raise NSLSolverError("Unexpected error: no response received.")

    @staticmethod
    def _handle_error_response(response: requests.Response) -> None:
        """Map an HTTP error response to the appropriate exception."""
        status = response.status_code

        try:
            body = response.json()
        except (ValueError, KeyError):
            body = {}

        message = body.get("error", body.get("message", response.text))

        exc_map = {
            400: SolveError,
            401: AuthenticationError,
            402: InsufficientBalanceError,
            403: TypeNotAllowedError,
            429: RateLimitError,
            503: BackendError,
        }
        cls = exc_map.get(status)
        if cls:
            raise cls(message=str(message), status_code=status, response_body=body)
        raise NSLSolverError(
            message=f"Unexpected API error (HTTP {status}): {message}",
            status_code=status,
            response_body=body,
        )

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "NSLSolver":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"NSLSolver(base_url={self._base_url!r})"
