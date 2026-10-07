import hashlib
import re
from typing import Any, Dict, List, Tuple


def make_fingerprint(rec: Dict[str, Any]) -> str:
    """
    Builds a deterministic fingerprint:
    - Books:  source + title
    - Quotes: source + author + first 50 chars of quote
    Lowercased, punctuation stripped, spaces collapsed, hashed with SHA-256.
    """
    source = rec.get("source") or ""
    title = rec.get("name_or_title") or ""
    author = rec.get("author") or ""

    if source == "Books to Scrape":
        key = f"{source} {title}"
    else:  # quotes
        key = f"{source} {author} {title[:50]}"

    key = re.sub(r"[^\w\s]", "", key.lower())
    key = " ".join(key.split())
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def find_duplicates(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Identifies and separates unique records from duplicates.
    Returns (unique_records, duplicate_records).
    """
    seen = set()
    unique = []
    dupes = []

    for rec in records:
        fp = make_fingerprint(rec)
        if fp in seen:
            dupes.append(rec)
        else:
            seen.add(fp)
            unique.append(rec)

    return unique, dupes