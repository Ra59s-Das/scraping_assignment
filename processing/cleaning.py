import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

# Maps word-based ratings to integer scores (1 to 5)
RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}


def clean_text(value: Optional[str]) -> Optional[str]:
    """Collapses spaces, tabs, newlines, and non-breaking spaces (\xa0). Empty becomes None."""
    if value is None:
        return None
    text = " ".join(str(value).replace("\xa0", " ").split())
    return text if text else None


def strip_quotes(value: Optional[str]) -> Optional[str]:
    """Strips leading/trailing curly or straight quotes from quote text."""
    cleaned = clean_text(value)
    if not cleaned:
        return None
    return cleaned.strip('“”"\'').strip()


def clean_price(raw: Any) -> Optional[float]:
    """Extracts numeric price as float (e.g., '£51.77' -> 51.77)."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return round(float(raw), 2)
    cleaned_str = str(raw).replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", cleaned_str)
    return round(float(match.group()), 2) if match else None


def clean_rating(raw: Any) -> Optional[int]:
    """Converts rating class words (e.g. 'star-rating Three') into integers 1 to 5."""
    if raw is None:
        return None
    if isinstance(raw, int) and 1 <= raw <= 5:
        return raw
    for word in str(raw).lower().split():
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(tags: Any) -> Optional[str]:
    """Lowercases, sorts, and joins tags with semicolons (e.g. 'books;reading')."""
    if not tags:
        return None
    if isinstance(tags, str):
        tag_list = [t.strip() for t in tags.split(";") if t.strip()]
    elif isinstance(tags, (list, tuple, set)):
        tag_list = [str(t).strip() for t in tags if str(t).strip()]
    else:
        return None

    cleaned = sorted(list({t.lower() for t in tag_list}))
    return ";".join(cleaned) if cleaned else None


def normalize_url(url: Optional[str]) -> Optional[str]:
    """Ensures URL is complete and begins with http:// or https://."""
    if not url:
        return None
    cleaned = str(url).strip()
    parsed = urlparse(cleaned)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return cleaned
    return None


def clean_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Applies all cleaning functions to a raw record dictionary."""
    is_quote = rec.get("source") == "Quotes to Scrape"
    title_raw = rec.get("name_or_title")
    title_cleaned = strip_quotes(title_raw) if is_quote else clean_text(title_raw)

    return {
        "source": clean_text(rec.get("source")),
        "source_url": normalize_url(rec.get("source_url")),
        "name_or_title": title_cleaned,
        "category": clean_text(rec.get("category")),
        "price": clean_price(rec.get("price")),
        "rating": clean_rating(rec.get("rating")),
        "author": clean_text(rec.get("author")),
        "tags": clean_tags(rec.get("tags")),
        "description": clean_text(rec.get("description")),
        "scraped_at": rec.get("scraped_at"),
    }