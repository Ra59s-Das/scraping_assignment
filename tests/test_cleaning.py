from processing.cleaning import (
    clean_text,
    strip_quotes,
    clean_price,
    clean_rating,
    clean_tags,
    normalize_url
)


def test_clean_price():
    assert clean_price("£51.77") == 51.77
    assert clean_price("1,234.50") == 1234.50
    assert clean_price(29.99) == 29.99
    assert clean_price("Free") is None
    assert clean_price(None) is None


def test_clean_rating():
    assert clean_rating("star-rating Three") == 3
    assert clean_rating("star-rating One") == 1
    assert clean_rating("Five") == 5
    assert clean_rating("Unknown") is None
    assert clean_rating(None) is None


def test_clean_text():
    assert clean_text("  Hello \n  World ") == "Hello World"
    assert clean_text("Non-breaking\xa0space") == "Non-breaking space"
    assert clean_text("") is None
    assert clean_text(None) is None


def test_strip_quotes():
    assert strip_quotes("“The world as we have created it...”") == "The world as we have created it..."
    assert strip_quotes('"A test quote"') == "A test quote"


def test_clean_tags():
    assert clean_tags(["books", "classic", "Books"]) == "books;classic"
    assert clean_tags("books; fiction ; books") == "books;fiction"
    assert clean_tags(None) is None


def test_normalize_url():
    assert normalize_url("https://books.toscrape.com/catalogue/page-1.html") == "https://books.toscrape.com/catalogue/page-1.html"
    assert normalize_url("ftp://not-supported.com") is None
    assert normalize_url("just-a-string") is None