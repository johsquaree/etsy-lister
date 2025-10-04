import random
import time
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def polite_get(url: str, delay_seconds: float = 1.0, timeout: int = 20) -> Optional[requests.Response]:
    time.sleep(delay_seconds + random.uniform(0, 0.5))
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        if resp.status_code == 200:
            return resp
        return None
    except requests.RequestException:
        return None


def get_soup(url: str, delay_seconds: float = 1.0) -> Optional[BeautifulSoup]:
    resp = polite_get(url, delay_seconds=delay_seconds)
    if not resp:
        return None
    return BeautifulSoup(resp.text, "html.parser")


def extract_text(el: Any) -> str:
    if not el:
        return ""
    return str(el.get_text(strip=True))

