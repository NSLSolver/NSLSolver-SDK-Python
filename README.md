# NSLSolver Python SDK

Python SDK for the [NSLSolver](https://nslsolver.com) captcha solving API.

## Installation

```bash
pip install nslsolver

# async support
pip install nslsolver[async]
```

## Quick Start

```python
from nslsolver import NSLSolver

solver = NSLSolver("your-api-key")

# Turnstile
result = solver.solve_turnstile(
    site_key="0x4AAAAAAAB...",
    url="https://example.com",
)
print(result.token)

# Cloudflare challenge (proxy required)
result = solver.solve_challenge(
    url="https://example.com/protected",
    proxy="http://user:pass@host:port",
)
print(result.cookies, result.user_agent)

# Balance
balance = solver.get_balance()
print(balance.balance, balance.max_threads, balance.allowed_types)
```

## Async

```python
import asyncio
from nslsolver import AsyncNSLSolver

async def main():
    async with AsyncNSLSolver("your-api-key") as solver:
        result = await solver.solve_turnstile(
            site_key="0x4AAAAAAAB...",
            url="https://example.com",
        )
        print(result.token)

asyncio.run(main())
```

## Error Handling

```python
from nslsolver import (
    NSLSolver,
    AuthenticationError,
    InsufficientBalanceError,
    RateLimitError,
    SolveError,
    NSLSolverError,
)

solver = NSLSolver("your-api-key")

try:
    result = solver.solve_turnstile(
        site_key="0x4AAAAAAAB...",
        url="https://example.com",
    )
except AuthenticationError:
    print("Bad API key.")
except InsufficientBalanceError:
    print("Top up your balance.")
except RateLimitError:
    print("Rate limited after all retries.")
except SolveError as e:
    print(f"Solve failed: {e.message}")
except NSLSolverError as e:
    print(f"API error (HTTP {e.status_code}): {e.message}")
```

Rate-limit (429) and backend (503) errors are retried automatically with exponential backoff before raising.

## Configuration

```python
solver = NSLSolver(
    api_key="your-api-key",
    base_url="https://api.nslsolver.com",  # default
    timeout=120,       # seconds (default: 120)
    max_retries=3,     # retries for 429/503 (default: 3)
)
```

Both clients support context managers (`with` / `async with`) for session cleanup.

## Requirements

- Python 3.8+
- `requests` (sync client)
- `aiohttp` (async client, optional)

## License

MIT
