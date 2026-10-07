import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(rec: Dict[str, Any]) -> List[str]:
    """
    Checks one cleaned record and returns a list of problem identifiers.
    An empty list indicates a valid record.
    """
    problems = []

    if rec.get("source") not in VALID_SOURCES:
        problems.append("unknown_source")

    if not rec.get("name_or_title"):
        problems.append("missing_name")

    if not str(rec.get("source_url") or "").startswith(("http://", "https://")):
        problems.append("invalid_url")

    price = rec.get("price")
    if price is not None and (not isinstance(price, (int, float)) or price < 0):
        problems.append("invalid_price")

    rating = rec.get("rating")
    if rating is not None and rating not in (1, 2, 3, 4, 5):
        problems.append("invalid_rating")

    return problems


def validate_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, int]]:
    """
    Validates a list of records.
    Returns (valid_records, rejected_records, reason_counts).
    """
    valid = []
    rejected = []
    reason_counts = {
        "unknown_source": 0,
        "missing_name": 0,
        "invalid_url": 0,
        "invalid_price": 0,
        "invalid_rating": 0
    }

    for rec in records:
        problems = validate_record(rec)
        if not problems:
            valid.append(rec)
        else:
            rec_with_errors = dict(rec)
            rec_with_errors["validation_errors"] = problems
            rejected.append(rec_with_errors)
            for p in problems:
                reason_counts[p] = reason_counts.get(p, 0) + 1
            logger.warning("Rejected record '%s': %s", rec.get("name_or_title"), problems)

    return valid, rejected, reason_counts