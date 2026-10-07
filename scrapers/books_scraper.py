from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BooksScraper(BaseScraper):
    """
    Scraper for Books to Scrape (https://books.toscrape.com/).
    Traverses dynamic pagination via 'li.next > a' across 50 pages (~1,000 books).
    """

    SOURCE_NAME = "Books to Scrape"
    START_URL = "https://books.toscrape.com/catalogue/page-1.html"

    def __init__(self, delay: float = 0.5):
        super().__init__(base_url="https://books.toscrape.com/", delay=delay)

    def scrape(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrapes books page by page following the 'next' button.
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

            articles = soup.select("article.product_pod")
            if not articles:
                logger.warning("[%s] No articles found on page %d.", self.SOURCE_NAME, page)
                break

            for article in articles:
                try:
                    record = self._parse_book(article, url)
                    if record:
                        records.append(record)
                except Exception as exc:
                    logger.warning("[%s] Error extracting book pod on page %d: %s", self.SOURCE_NAME, page, exc)

            # Dynamic pagination: follows 'next' link rather than hardcoding page counts
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page += 1

        logger.info("[%s] Scraping finished. Total collected raw records: %d", self.SOURCE_NAME, len(records))
        return records

    def _parse_book(self, article, page_url: str) -> Dict[str, Any]:
        """
        Safely extracts book fields.
        Crucial observation: Visible text is truncated with '...',
        so full title must be extracted from the 'title' attribute of <a>.
        """
        link = article.select_one("h3 > a")
        price = article.select_one("p.price_color")
        rating = article.select_one("p.star-rating")
        availability = article.select_one("p.availability")

        # Full title extraction
        title = link.get("title") if link else None
        href = urljoin(page_url, link["href"]) if link and link.get("href") else None
        price_raw = price.get_text() if price else None

        # Ratings are stored as CSS classes, e.g. class="star-rating Three"
        rating_raw = " ".join(rating.get("class", [])) if rating else None
        avail_text = availability.get_text(strip=True) if availability else None

        return {
            "source": self.SOURCE_NAME,
            "source_url": href or page_url,
            "name_or_title": title,
            "category": None,  # Not displayed on catalog page; left None per specification
            "price": price_raw,
            "rating": rating_raw,
            "author": None,
            "tags": None,
            "description": f"Availability: {avail_text}" if avail_text else None,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }