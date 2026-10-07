from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class QuotesScraper(BaseScraper):
    """
    Scraper for Quotes to Scrape (https://quotes.toscrape.com/).
    Traverses dynamic pagination via 'li.next > a' across 10 pages (100 quotes).
    """

    SOURCE_NAME = "Quotes to Scrape"
    START_URL = "https://quotes.toscrape.com/"

    def __init__(self, delay: float = 0.5):
        super().__init__(base_url="https://quotes.toscrape.com/", delay=delay)

    def scrape(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrapes quotes page by page following the 'next' button.
        """
        url = self.START_URL
        page = 1
        records: List[Dict[str, Any]] = []

        while url:
            if max_pages and page > max_pages:
                logger.info("[%s] Reached maximum requested pages limit (%d).", self.SOURCE_NAME, max_pages)
                break

            logger.info("[%s] Page %d: %s", self.SOURCE_NAME, page, url)
            soup = self.fetch_soup(url)
            if not soup:
                logger.error("[%s] Failed to load page %s. Stopping source traversal.", self.SOURCE_NAME, url)
                break

            quote_divs = soup.select("div.quote")
            if not quote_divs:
                logger.warning("[%s] No quotes found on page %d.", self.SOURCE_NAME, page)
                break

            for div in quote_divs:
                try:
                    record = self._parse_quote(div, url)
                    if record:
                        records.append(record)
                except Exception as exc:
                    logger.warning("[%s] Error extracting quote item on page %d: %s", self.SOURCE_NAME, page, exc)

            # Dynamic pagination: follows 'next' link
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page += 1

        logger.info("[%s] Scraping finished. Total collected raw records: %d", self.SOURCE_NAME, len(records))
        return records

    def _parse_quote(self, div, page_url: str) -> Dict[str, Any]:
        """
        Safely extracts quote fields, author page URL, and tag list.
        """
        text_el = div.select_one("span.text")
        author_el = div.select_one("small.author")
        author_link = div.select_one('a[href^="/author/"]')
        tag_elements = div.select("a.tag")

        quote_text = text_el.get_text() if text_el else None
        author_name = author_el.get_text() if author_el else None
        
        # Absolute URL pointing to author details
        source_url = urljoin(page_url, author_link["href"]) if author_link and author_link.get("href") else page_url
        raw_tags = [t.get_text() for t in tag_elements]

        return {
            "source": self.SOURCE_NAME,
            "source_url": source_url,
            "name_or_title": quote_text,
            "category": "Quotes",  # Standardized category label for quotes
            "price": None,
            "rating": None,
            "author": author_name,
            "tags": raw_tags,  # Raw list, cleaned and joined in processing/cleaning.py
            "description": None,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }