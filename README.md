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

# Kasada
from nslsolver import KasadaConfig

result = solver.solve_kasada(
    url="https://example.com/api",
    user_agent="Mozilla/5.0 ...",
    ua_version=131,
    kasada_config=KasadaConfig(
        p_js_path="/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js",
        fp_host="https://fp.example.com",
        tl_host="https://tl.example.com",
    ),
)
print(result.headers)
print(result.ct, result.cd)

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

## Documentation

For more information, check out the full documentation at https://docs.nslsolver.com

## License

MIT
