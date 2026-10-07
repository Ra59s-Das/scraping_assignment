from processing.deduplication import find_duplicates, make_fingerprint


def test_duplicates_ignore_case_and_spaces():
    base = {"source": "Books to Scrape", "author": None}
    records = [
        {**base, "name_or_title": "Example Book Title"},
        {**base, "name_or_title": "  Example Book Title "},
        {**base, "name_or_title": "EXAMPLE BOOK TITLE"},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 1 and len(dupes) == 2


def test_quotes_fingerprint_uses_author_and_prefix():
    base = {"source": "Quotes to Scrape", "author": "Albert Einstein"}
    rec1 = {**base, "name_or_title": "Insanity is doing the same thing over and over again and expecting different results."}
    rec2 = {**base, "name_or_title": "Insanity is doing the same thing over and over again!"}

    fp1 = make_fingerprint(rec1)
    fp2 = make_fingerprint(rec2)
    assert fp1 == fp2