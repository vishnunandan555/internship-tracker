"""Thin HTTP helper with retries, exponential backoff with jitter, and thread-safe session pooling."""
import random
import threading
import time
from typing import Any, Optional

import requests

USER_AGENT_POOL = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
]
USER_AGENT = USER_AGENT_POOL[0]

DEFAULT_TIMEOUT = 15
RETRIES = 3
BASE_BACKOFF = 2.0
MAX_BACKOFF = 30.0
RETRIABLE_CODES = {429, 500, 502, 503, 504}

_thread_local = threading.local()


def get_user_agent() -> str:
    """Return a randomized realistic browser User-Agent from the pool."""
    return random.choice(USER_AGENT_POOL)


def get_session() -> requests.Session:
    """Return a thread-local requests.Session for connection reuse and pooling."""
    if not hasattr(_thread_local, "session") or _thread_local.session is None:
        _thread_local.session = requests.Session()
    return _thread_local.session


def close_thread_session() -> None:
    """Close and tear down the current thread's Session if active."""
    sess = getattr(_thread_local, "session", None)
    if sess is not None:
        try:
            sess.close()
        except Exception:
            pass
        _thread_local.session = None


def set_thread_timeout(timeout: Optional[int]) -> None:
    """Set the active company's custom timeout for the current worker thread."""
    _thread_local.timeout = timeout


def get_thread_timeout() -> int:
    """Get the active thread timeout or fallback to DEFAULT_TIMEOUT."""
    return getattr(_thread_local, "timeout", None) or DEFAULT_TIMEOUT


def _backoff(attempt: int) -> float:
    """Calculate exponential backoff delay with ±20% jitter."""
    delay = min(BASE_BACKOFF * (2 ** attempt), MAX_BACKOFF)
    return delay * random.uniform(0.8, 1.2)


def _request(
    method: str,
    url: str,
    *,
    accept: str,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    json_body: Optional[dict] = None,
    data: Any = None,
    cookies: Any = None,
    session: Optional[requests.Session] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> requests.Response:
    default_ua = getattr(_thread_local, "user_agent", None)
    if not default_ua:
        default_ua = get_user_agent()
        _thread_local.user_agent = default_ua

    h = {"User-Agent": default_ua, "Accept": accept}
    if headers:
        h.update(headers)
    client = session or get_session()
    eff_timeout = timeout if timeout != DEFAULT_TIMEOUT else get_thread_timeout()
    last_err: Optional[Exception] = None

    for attempt in range(RETRIES):
        try:
            resp = client.request(
                method,
                url,
                headers=h,
                params=params,
                json=json_body,
                data=data,
                cookies=cookies,
                timeout=eff_timeout,
            )
            if resp.status_code in RETRIABLE_CODES:
                raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
            resp.raise_for_status()
            return resp
        except (requests.RequestException, ValueError) as err:
            last_err = err
            if attempt < RETRIES - 1:
                time.sleep(_backoff(attempt))

    raise RuntimeError(
        f"request failed after {RETRIES} attempts: {method} {url} ({last_err})"
    )


def request_json(
    method: str,
    url: str,
    *,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    json_body: Optional[dict] = None,
    data: Any = None,
    cookies: Any = None,
    session: Optional[requests.Session] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """Perform a request expecting a JSON response. Retries on 5xx/429/network errors."""
    return _request(
        method,
        url,
        accept="application/json",
        headers=headers,
        params=params,
        json_body=json_body,
        data=data,
        cookies=cookies,
        session=session,
        timeout=timeout,
    ).json()


def request_text(
    method: str,
    url: str,
    *,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    data: Any = None,
    cookies: Any = None,
    session: Optional[requests.Session] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Perform a request expecting text/HTML response. Retries on 5xx/429/network errors."""
    return _request(
        method,
        url,
        accept="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        headers=headers,
        params=params,
        data=data,
        cookies=cookies,
        session=session,
        timeout=timeout,
    ).text

