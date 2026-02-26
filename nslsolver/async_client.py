"""Async NSLSolver client (requires aiohttp)."""

import asyncio
import logging
from typing import Any, Dict, Optional

try:
    import aiohttp
except ImportError:
    raise ImportError(
        "The 'aiohttp' package is required for the async client. "
        "Install it with: pip install nslsolver[async]"
    )

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

_RETRYABLE_EXCEPTIONS = (RateLimitError, BackendError)


class AsyncNSLSolver:
    """Async client for the NSLSolver API."""

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
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers = {
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
            "User-Agent": "nslsolver-python/1.0.0 (async)",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers=self._headers,
                timeout=self._timeout,
            )
        return self._session

    # -- Public API ----------------------------------------------------------

    async def solve_turnstile(
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

        data = await self._request("POST", "/solve", json_body=payload)

        return TurnstileResult(
            token=data["token"],
            type=data.get("type", "turnstile"),
        )

    async def solve_challenge(
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

        data = await self._request("POST", "/solve", json_body=payload)

        return ChallengeResult(
            cookies=data.get("cookies", {}),
            user_agent=data.get("user_agent", ""),
            type=data.get("type", "challenge"),
        )

    async def get_balance(self) -> BalanceResult:
        """Retrieve current account balance."""
        data = await self._request("GET", "/balance")

        known_keys = {"balance", "max_threads", "allowed_types"}
        extra = {k: v for k, v in data.items() if k not in known_keys}

        return BalanceResult(
            balance=float(data["balance"]),
            max_threads=int(data["max_threads"]),
            allowed_types=list(data.get("allowed_types", [])),
            extra=extra,
        )

    # -- Internal ------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute an HTTP request with retries on transient errors."""
        url = f"{self._base_url}{path}"
        last_exc: Optional[Exception] = None
        backoff = _INITIAL_BACKOFF
        session = await self._get_session()

        for attempt in range(self._max_retries + 1):
            try:
                async with session.request(
                    method=method,
                    url=url,
                    json=json_body,
                ) as response:
                    if response.status == 200:
                        return await response.json()  # type: ignore[no-any-return]

                    response_text = await response.text()
                    self._handle_error_response(response.status, response_text)

            except _RETRYABLE_EXCEPTIONS as exc:
                last_exc = exc
            except asyncio.TimeoutError:
                last_exc = NSLSolverError("Request timed out.")
            except aiohttp.ClientConnectionError:
                last_exc = NSLSolverError("Connection error.")
            else:
                break  # pragma: no cover

            if attempt < self._max_retries:
                sleep_time = min(backoff, _MAX_BACKOFF)
                logger.warning(
                    "%s on attempt %d/%d, retrying in %.1fs",
                    last_exc,
                    attempt + 1,
                    self._max_retries + 1,
                    sleep_time,
                )
                await asyncio.sleep(sleep_time)
                backoff *= _BACKOFF_MULTIPLIER
            else:
                raise last_exc  # type: ignore[misc]

        if last_exc is not None:
            raise last_exc
        raise NSLSolverError("Unexpected error: no response received.")

    @staticmethod
    def _handle_error_response(status: int, response_text: str) -> None:
        """Map an HTTP error response to the appropriate exception."""
        import json

        try:
            body = json.loads(response_text)
        except (ValueError, KeyError):
            body = {}

        message = body.get("error", body.get("message", response_text))

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

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "AsyncNSLSolver":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def __repr__(self) -> str:
        return f"AsyncNSLSolver(base_url={self._base_url!r})"
