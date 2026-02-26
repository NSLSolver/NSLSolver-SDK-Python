"""Response types for the NSLSolver API."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TurnstileResult:
    """Result of a Turnstile captcha solve."""

    token: str
    type: str = "turnstile"

    def __str__(self) -> str:
        return self.token


@dataclass(frozen=True)
class ChallengeResult:
    """Result of a Cloudflare challenge solve."""

    cookies: Dict[str, str]
    user_agent: str
    type: str = "challenge"

    @property
    def cf_clearance(self) -> Optional[str]:
        return self.cookies.get("cf_clearance")


@dataclass(frozen=True)
class BalanceResult:
    """Account balance and capability info."""

    balance: float
    max_threads: int
    allowed_types: List[str]
    extra: Dict[str, object] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"Balance: {self.balance}, "
            f"Max Threads: {self.max_threads}, "
            f"Allowed Types: {self.allowed_types}"
        )
