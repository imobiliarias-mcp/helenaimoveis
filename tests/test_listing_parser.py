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


def test_listing_parser_exposes_absolute_public_url_and_preserves_path():
    """Resolve the property URL while retaining the original relative path."""
    html_path = FIXTURES_DIR / "search_single.html"
    content = html_path.read_text(encoding="iso-8859-1")
    listing = ListingParser().parse(content)[0]

    assert listing.identity.url_path == (
        "/imovel/4356012/apartamento-locacao-timoteo-mg-centro-norte"
    )
    assert getattr(listing, "url", None) == (
        "https://www.helenaimoveis.com.br"
        "/imovel/4356012/apartamento-locacao-timoteo-mg-centro-norte"
    )


def test_listing_parser_rejects_non_public_property_links():
    """Reject unsupported property URL schemes during parsing."""
    import pytest

    content = (FIXTURES_DIR / "search_single.html").read_text(encoding="iso-8859-1")
    invalid_links = (
        "javascript:alert(1)",
        "https://evil.example/imovel/4356012/apartamento",
        "https://www.helenaimoveis.com.br/imagens/4356012.jpg",
        "https://www.helenaimoveis.com.br/imovel/locacao/todos/timoteo",
        "https://www.helenaimoveis.com.br/",
    )
    for invalid_link in invalid_links:
        invalid_content = content.replace(
            'data-link="/imovel/4356012/apartamento-locacao-timoteo-mg-centro-norte"',
            f'data-link="{invalid_link}"',
        ).replace('href="/imovel/4356012"', f'href="{invalid_link}"')
        with pytest.raises(ValueError, match="invalid public URL"):
            ListingParser().parse(invalid_content)


def test_listing_collection_serializes_url_and_pagination():
    """Serialize public URLs without losing search pagination metadata."""
    content = (FIXTURES_DIR / "search_single.html").read_text(encoding="iso-8859-1")
    collection = ListingParser().parse(content, current_page=4)
    serialized = collection.to_dictionary()

    assert serialized["items"][0]["url"].startswith(
        "https://www.helenaimoveis.com.br/imovel/4356012/"
    )
    assert serialized["items"][0]["url_path"].startswith("/imovel/4356012/")
    assert serialized["current_page"] == 4
    assert serialized["has_next_page"] is False


def test_listing_parser_normalizes_absolute_and_protocol_relative_links():
    """Preserve native link forms and identifying query parameters."""
    route = "/imovel/4356012/apartamento-locacao-timoteo-mg-centro-norte"
    path = f"{route}?id=608"
    source_route = route
    content = (FIXTURES_DIR / "search_single.html").read_text(encoding="iso-8859-1")

    for source in (
        f"https://www.helenaimoveis.com.br{path}",
        f"//www.helenaimoveis.com.br{path}",
    ):
        linked_content = content.replace(
            f'data-link="{source_route}"', f'data-link="{source}"'
        )
        listing = ListingParser().parse(linked_content)[0]
        assert listing.identity.url_path == source
        assert listing.url == f"https://www.helenaimoveis.com.br{path}"


def test_listing_parser_uses_anchor_fallback_and_rejects_missing_urls():
    """Use only the card's real anchor when canonical data-link is absent."""
    import pytest

    from helena_research.domain.exceptions import InvalidPublicPropertyUrlError

    content = (FIXTURES_DIR / "search_single.html").read_text(encoding="iso-8859-1")
    detail_path = (
        "/imovel/4356012/apartamento-locacao-timoteo-mg-centro-norte"
    )
    no_data_link = content.replace(f' data-link="{detail_path}"', "")
    listing = ListingParser().parse(no_data_link)[0]
    assert listing.identity.url_path == detail_path
    assert listing.url == f"https://www.helenaimoveis.com.br{detail_path}"

    no_recoverable_link = no_data_link.replace(f'href="{detail_path}"', "")
    with pytest.raises(InvalidPublicPropertyUrlError, match="recoverable"):
        ListingParser().parse(no_recoverable_link)


def test_listing_collection_serializes_zero_and_multiple_results():
    """Preserve empty and multi-result collection metadata while serializing."""
    empty = ListingParser().parse("<html></html>", current_page=2).to_dictionary()
    content = (FIXTURES_DIR / "search_multi.html").read_text(encoding="iso-8859-1")
    multiple = ListingParser().parse(content, current_page=2).to_dictionary()

    assert empty == {"items": [], "current_page": 2, "has_next_page": False}
    assert len(multiple["items"]) == 15
    assert multiple["current_page"] == 2
    assert all(item["url"].startswith("https://www.helenaimoveis.com.br/") for item in multiple["items"])


def test_research_runner_prints_public_property_url(monkeypatch, capsys):
    """Print public URLs beside listing output in the existing runner."""
    from types import SimpleNamespace

    from scripts import run_research

    content = (FIXTURES_DIR / "search_single.html").read_text(encoding="iso-8859-1")
    results = ListingParser().parse(content)

    class StubPhotos:
        def __len__(self):
            return 1

        def first_photo(self):
            return "photo.jpg"

    detail = SimpleNamespace(
        overview=SimpleNamespace(title="Title", reference_code="Ref"),
        location=SimpleNamespace(address="Address", neighborhood="Center"),
        pricing=SimpleNamespace(formatted_text="R$ 1.200", amount=1200, iptu="", condo_fee=""),
        specs=SimpleNamespace(bedrooms=2, bathrooms=1, parking_spaces=1),
        characteristics=(),
        photos=StubPhotos(),
    )

    class StubService:
        def search_by_url(self, target_url):
            return results

        def search_rentals(self, criteria):
            return results

        def get_property_detail(self, property_id):
            return detail

        def get_property_photos(self, property_id):
            return ("photo.jpg",)

    monkeypatch.setattr(run_research, "HelenaResearchService", StubService)
    run_research.main()

    assert capsys.readouterr().out.count("Link: https://www.helenaimoveis.com.br/imovel/4356012/") == 2


def test_listing_serializer_rejects_missing_and_relative_public_urls():
    """Reject manually constructed listings without an absolute public URL."""
    from dataclasses import replace

    import pytest

    from helena_research.domain.exceptions import InvalidPublicPropertyUrlError

    content = (FIXTURES_DIR / "search_single.html").read_text(encoding="iso-8859-1")
    listing = ListingParser().parse(content)[0]
    for url in ("", "/imovel/4356012"):
        with pytest.raises(InvalidPublicPropertyUrlError, match="4356012"):
            replace(listing, url=url).to_dictionary()


def test_malformed_card_links_raise_the_local_public_url_exception():
    """Wrap malformed canonical links and detail anchors with URL context."""
    import pytest

    from helena_research.domain.exceptions import InvalidPublicPropertyUrlError

    content = (FIXTURES_DIR / "search_single.html").read_text(encoding="iso-8859-1")
    valid_link = "/imovel/4356012/apartamento-locacao-timoteo-mg-centro-norte"
    malformed_link = "https://[broken/imovel/4356012"
    canonical_html = content.replace(
        f'data-link="{valid_link}"', f'data-link="{malformed_link}"'
    )
    anchor_html = content.replace(f' data-link="{valid_link}"', "").replace(
        f'href="{valid_link}"', f'href="{malformed_link}"'
    )

    for invalid_html in (canonical_html, anchor_html):
        with pytest.raises(InvalidPublicPropertyUrlError, match="malformed public URL") as error:
            ListingParser().parse(invalid_html)
        assert malformed_link in str(error.value)
