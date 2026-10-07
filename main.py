import argparse
import csv
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import time
from typing import Dict, List

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_records
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

CSV_COLUMNS = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at"
]


def setup_logging(log_file: Path) -> None:
    """Configures dual logging to console and logs/scraper.log."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(str(log_file), mode="w", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def write_csv(records: List[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_summary(stats: Dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Multi-Source Scraping Pipeline")
    parser.add_argument("--books-pages", type=int, default=None, help="Optional max pages for Books")
    parser.add_argument("--quotes-pages", type=int, default=None, help="Optional max pages for Quotes")
    args = parser.parse_args()

    project_root = Path(__file__).parent
    log_path = project_root / "logs" / "scraper.log"
    csv_path = project_root / "output" / "final_dataset.csv"
    summary_path = project_root / "output" / "summary_report.json"

    setup_logging(log_path)
    logger = logging.getLogger("Pipeline")

    start_time_iso = datetime.now(timezone.utc).isoformat()
    start_time = time.time()
    logger.info("=== ETL PIPELINE STARTED ===")

    # 1. Scraping (each source isolated with try/except)
    books_scraper = BooksScraper()
    quotes_scraper = QuotesScraper()

    raw_books = []
    raw_quotes = []

    try:
        raw_books = books_scraper.scrape(max_pages=args.books_pages)
    except Exception as exc:
        logger.error("BooksScraper failed unexpectedly: %s", exc, exc_info=True)

    try:
        raw_quotes = quotes_scraper.scrape(max_pages=args.quotes_pages)
    except Exception as exc:
        logger.error("QuotesScraper failed unexpectedly: %s", exc, exc_info=True)

    collected_per_source = {
        "Books to Scrape": len(raw_books),
        "Quotes to Scrape": len(raw_quotes)
    }
    all_raw = raw_books + raw_quotes
    logger.info("Scraping completed. Books: %d, Quotes: %d. Total: %d",
                len(raw_books), len(raw_quotes), len(all_raw))

    # 2. Cleaning
    logger.info("Cleaning records...")
    cleaned_records = [clean_record(r) for r in all_raw]
    cleaned_per_source = {
        "Books to Scrape": sum(1 for r in cleaned_records if r.get("source") == "Books to Scrape"),
        "Quotes to Scrape": sum(1 for r in cleaned_records if r.get("source") == "Quotes to Scrape")
    }

    # 3. Validation
    logger.info("Validating records...")
    valid_records, rejected_records, rejected_by_reason = validate_records(cleaned_records)
    logger.info("Validation complete. Valid: %d, Rejected: %d", len(valid_records), len(rejected_records))

    # 4. Deduplication
    logger.info("Deduplicating valid records...")
    unique_records, duplicate_records = find_duplicates(valid_records)
    logger.info("Deduplication complete. Unique retained: %d, Duplicates found: %d",
                len(unique_records), len(duplicate_records))

    # 5. Output Generation
    write_csv(unique_records, csv_path)
    logger.info("Saved CSV dataset with %d rows to %s", len(unique_records), csv_path)

    duration_seconds = round(time.time() - start_time, 2)
    end_time_iso = datetime.now(timezone.utc).isoformat()

    # Reconciled metrics
    summary_data = {
        "start_time": start_time_iso,
        "end_time": end_time_iso,
        "duration_seconds": duration_seconds,
        "collected_per_source": collected_per_source,
        "cleaned_per_source": cleaned_per_source,
        "rejected_by_reason": rejected_by_reason,
        "total_rejected": len(rejected_records),
        "duplicates_detected": len(duplicate_records),
        "final_record_count": len(unique_records),
        "reconciliation_check": (
            len(all_raw) - len(rejected_records) - len(duplicate_records) == len(unique_records)
        )
    }

    write_summary(summary_data, summary_path)
    logger.info("Saved summary report to %s", summary_path)
    logger.info("=== PIPELINE FINISHED IN %.2f SECONDS ===", duration_seconds)


if __name__ == "__main__":
    main()