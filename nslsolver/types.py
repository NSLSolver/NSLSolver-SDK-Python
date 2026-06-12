"""Response types for the NSLSolver API."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True)
class TurnstileResult:
    """Result of a Turnstile captcha solve."""

    token: str
    cost: float = 0.0
    solve_time_ms: Optional[int] = None
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
class RecaptchaV3Result:
    """Result of a reCAPTCHA v3 (and reCAPTCHA Enterprise) solve.

    ``token`` is the verification token to submit to the target site. ``action``
    echoes the action the token was bound to (when returned). ``type`` reflects
    the response discriminator as returned by the API (the API returns the
    hyphenated slug ``recaptcha-v3``, not the request discriminator
    ``recaptchav3``).
    """

    token: str
    action: Optional[str] = None
    cost: float = 0.0
    type: Optional[str] = None

    def __str__(self) -> str:
        return self.token


@dataclass(frozen=True)
class BalanceResult:
    """Account balance for the API key.

    The documented ``GET /balance`` response is ``{balance, currency}``. Any
    additional plan/usage fields the API may return (e.g. ``unlimited``,
    ``allowed_types``, CPM counters) are preserved verbatim in ``extra``.
    """

    balance: float
    currency: str = "USD"
    extra: Dict[str, object] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Balance: {self.balance} {self.currency}"
