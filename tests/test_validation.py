from processing.validation import validate_record, validate_records


def test_valid_book_record():
    rec = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/book1",
        "name_or_title": "Clean Code",
        "price": 45.0,
        "rating": 5
    }
    assert validate_record(rec) == []


def test_invalid_sources_and_urls():
    rec = {
        "source": "Unauthorized Source",
        "source_url": "bad_link",
        "name_or_title": "",
        "price": -5.0,
        "rating": 9
    }
    problems = validate_record(rec)
    assert "unknown_source" in problems
    assert "missing_name" in problems
    assert "invalid_url" in problems
    assert "invalid_price" in problems
    assert "invalid_rating" in problems


def test_validate_records_partition():
    records = [
        {"source": "Books to Scrape", "source_url": "https://books.toscrape.com", "name_or_title": "Book 1", "price": 10.0, "rating": 3},
        {"source": "Invalid", "source_url": "https://books.toscrape.com", "name_or_title": "Book 2"}
    ]
    valid, rejected, counts = validate_records(records)
    assert len(valid) == 1
    assert len(rejected) == 1
    assert counts["unknown_source"] == 1