"""Unit tests for search listing HTML parser."""

from pathlib import Path
from helena_research.parsers.listing_parser import ListingParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_single_listing() -> None:
    """Test parsing search page with single target property."""
    html_path = FIXTURES_DIR / "search_single.html"
    content = html_path.read_text(encoding="iso-8859-1")
    parser = ListingParser()
    collection = parser.parse(content, current_page=1)

    assert len(collection) == 1
    assert not collection.has_next_page
    assert not collection.is_empty()

    item = collection[0]
    assert item.identity.property_id == "4356012"
    assert "Centro Norte" in item.location.neighborhood
    assert item.location.city == "Timóteo"
    assert item.price_text == "R$1.200"
    assert item.specs.bedrooms == 2
    assert item.specs.bathrooms == 1
    assert item.specs.parking_spaces == 1
    assert item.reference_code == "636"
    assert item.thumbnail_url is not None


def test_parse_multi_listings() -> None:
    """Test parsing search page with 15 properties."""
    html_path = FIXTURES_DIR / "search_multi.html"
    content = html_path.read_text(encoding="iso-8859-1")
    parser = ListingParser()
    collection = parser.parse(content, current_page=1)

    assert len(collection) == 15
    first = collection[0]
    assert first.identity.property_id == "4271522"
    assert first.price_text == "R$650"
    assert first.location.neighborhood == "RECANTO VERDE"
