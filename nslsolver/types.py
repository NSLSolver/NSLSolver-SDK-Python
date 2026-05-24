"""Response types for the NSLSolver API."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TurnstileResult:
    """Result of a Turnstile captcha solve."""

    token: str
    cost: float = 0.0
    type: str = "turnstile"

    def __str__(self) -> str:
        return self.token


@dataclass(frozen=True)
class ChallengeResult:
    """Result of a Cloudflare challenge solve."""

    cookies: Dict[str, str]
    user_agent: str
    token: Optional[str] = None
    cost: float = 0.0
    type: str = "challenge"

    @property
    def cf_clearance(self) -> Optional[str]:
        return self.cookies.get("cf_clearance")


@dataclass(frozen=True)
class KasadaConfig:
    """Kasada endpoint configuration."""

    p_js_path: str
    fp_host: str
    tl_host: str
    cd_constant: Optional[str] = None


@dataclass(frozen=True)
class KasadaResult:
    """Result of a Kasada solve."""

    headers: Dict[str, str]
    cost: float = 0.0
    type: str = "kasada"

    @property
    def ct(self) -> Optional[str]:
        return self.headers.get("x-kpsdk-ct")

    @property
    def cd(self) -> Optional[str]:
        return self.headers.get("x-kpsdk-cd")

    @property
    def v(self) -> Optional[str]:
        return self.headers.get("x-kpsdk-v")

    @property
    def h(self) -> Optional[str]:
        return self.headers.get("x-kpsdk-h")


@dataclass(frozen=True)
class AkamaiResult:
    """Result of an Akamai Bot Manager solve."""

    cookies: Dict[str, str]
    cost: float = 0.0
    type: str = "akamai"

    @property
    def abck(self) -> Optional[str]:
        return self.cookies.get("_abck")

    @property
    def bm_sz(self) -> Optional[str]:
        return self.cookies.get("bm_sz")


@dataclass(frozen=True)
class BalanceResult:
    """Account balance, plan flags, and live CPM (captchas-per-minute) usage."""

    balance: float
    unlimited: bool
    allowed_types: List[str]
    max_cpm: int
    current_cpm: int
    cpm_limit: int
    unlimited_expires_at: Optional[str] = None
    extra: Dict[str, object] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"Balance: {self.balance}, "
            f"Unlimited: {self.unlimited}, "
            f"CPM: {self.current_cpm}/{self.cpm_limit}, "
            f"Allowed Types: {self.allowed_types}"
        )
