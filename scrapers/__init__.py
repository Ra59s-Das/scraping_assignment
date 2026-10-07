"""
Scrapers package.
Exports the base scraper and individual source scrapers for Books and Quotes.
"""

from .base_scraper import BaseScraper, create_session
from .books_scraper import BooksScraper
from .quotes_scraper import QuotesScraper

__all__ = ["BaseScraper", "create_session", "BooksScraper", "QuotesScraper"]