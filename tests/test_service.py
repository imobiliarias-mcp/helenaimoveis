"""Unit tests for service facade with mock HTTP transport."""

from pathlib import Path
from helena_research.application.service import (
    HelenaResearchService,
    ParserCoordinator,
    TransportCoordinator,
)
from helena_research.domain.criteria import SearchCriteria
from helena_research.infrastructure.http_client import HttpResponse
from helena_research.infrastructure.url_builder import UrlBuilder
from helena_research.parsers.detail_parser import DetailParser
from helena_research.parsers.listing_parser import ListingParser
from helena_research.parsers.photo_parser import PhotoParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class MockHttpClient:
    """Mock client returning fixture contents."""

    def __init__(self) -> None:
        """Initialize mock responses."""
        self._search_html = (FIXTURES_DIR / "search_single.html").read_text(encoding="iso-8859-1")
        self._detail_html = (FIXTURES_DIR / "detail_4356012.html").read_text(encoding="iso-8859-1")
        self._photos_json = '{"0":{"codigo_imo":"4356012","arquivo_imm":"mock.jpg"}}'

    def get(self, url: str) -> HttpResponse:
        """Route mock response by URL."""
        if "lista_imoveis_fotos" in url:
            return HttpResponse(status_code=200, text=self._photos_json, final_url=url)
        if "/imovel/4356012" in url:
            return HttpResponse(status_code=200, text=self._detail_html, final_url=url)
        return HttpResponse(status_code=200, text=self._search_html, final_url=url)


def test_service_search_rentals() -> None:
    """Test service rental search workflow."""
    mock_client = MockHttpClient()
    transport = TransportCoordinator(http_client=mock_client, url_builder=UrlBuilder())
    service = HelenaResearchService(transport=transport)

    criteria = SearchCriteria.create_rental(city="timoteo", bedrooms=2)
    results = service.search_rentals(criteria)

    assert len(results) == 1
    assert results[0].identity.property_id == "4356012"


def test_service_property_detail() -> None:
    """Test service detail retrieval workflow."""
    mock_client = MockHttpClient()
    transport = TransportCoordinator(http_client=mock_client, url_builder=UrlBuilder())
    service = HelenaResearchService(transport=transport)

    detail = service.get_property_detail("4356012")
    assert detail.overview.property_id == "4356012"
    assert detail.pricing.amount == 1200.0


def test_service_photos() -> None:
    """Test service photos retrieval workflow."""
    mock_client = MockHttpClient()
    transport = TransportCoordinator(http_client=mock_client, url_builder=UrlBuilder())
    service = HelenaResearchService(transport=transport)

    photos = service.get_property_photos("4356012")
    assert len(photos) == 1
    assert "mock.jpg" in photos[0]
