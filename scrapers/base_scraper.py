import logging
import time
from typing import Optional
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    """
    Creates a requests.Session configured with:
    - Custom User-Agent header (Stage 3 requirement).
    - Exponential backoff retrying on HTTP 429, 500, 502, 503, 504.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "ScrapingAssignment/1.0 (learning project)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })

    retries = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class BaseScraper:
    """
    Shared base class for all scrapers.
    Handles network requests, rate limiting, and character encoding safety.
    """

    def __init__(self, base_url: str, delay: float = 0.5, timeout: int = 10):
        self.base_url = base_url
        self.delay = delay
        self.timeout = timeout
        self.session = create_session()

    def fetch_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetches an HTML page, enforces polite delay, sets utf-8 encoding
        (preventing '£' from turning into 'Â£'), and parses with lxml.
        Returns None if request fails after retries.
        """
        time.sleep(self.delay)  # 0.5s polite pause between requests
        try:
            logger.info("Fetching: %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"  # Preserves currency symbols
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None

    def absolute_url(self, relative_url: str) -> str:
        """Converts relative link to an absolute URL."""
        return urljoin(self.base_url, relative_url)