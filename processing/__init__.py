"""
Processing package.
Exports data cleaning, validation, and deduplication modules.
"""

from .cleaning import (
    clean_record,
    clean_text,
    strip_quotes,
    clean_price,
    clean_rating,
    clean_tags,
    normalize_url
)
from .validation import validate_record, validate_records
from .deduplication import make_fingerprint, find_duplicates

__all__ = [
    "clean_record",
    "clean_text",
    "strip_quotes",
    "clean_price",
    "clean_rating",
    "clean_tags",
    "normalize_url",
    "validate_record",
    "validate_records",
    "make_fingerprint",
    "find_duplicates",
]