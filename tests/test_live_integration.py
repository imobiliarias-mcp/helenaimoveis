"""Live integration tests hitting helenaimoveis.com.br endpoints."""

import pytest
from helena_research.application.service import HelenaResearchService
from helena_research.domain.criteria import SearchCriteria
from helena_research.domain.enums import PropertyType, SortOrder
from helena_research.domain.exceptions import PropertyNotFoundError


@pytest.fixture
def live_service() -> HelenaResearchService:
    """Fixture providing service configured with live network client."""
    return HelenaResearchService()


def test_live_search_target_url(live_service: HelenaResearchService) -> None:
    """Verify exact target URL from user prompt."""
    target_url = "https://www.helenaimoveis.com.br/imovel/locacao/todos/timoteo/?&dormitorios=2"
    results = live_service.search_by_url(target_url)

    assert len(results) >= 1
    assert results[0].identity.property_id == "4356012"
    assert results[0].specs.bedrooms == 2
    assert results[0].reference_code == "636"


def test_live_search_rentals_criteria(live_service: HelenaResearchService) -> None:
    """Verify search constructed via typed SearchCriteria."""
    criteria = SearchCriteria.create_rental(
        city="timoteo",
        property_type=PropertyType.TODOS,
        bedrooms=2,
    )
    results = live_service.search_rentals(criteria)

    assert len(results) >= 1
    assert results[0].identity.property_id == "4356012"


def test_live_search_all_timoteo_rentals(live_service: HelenaResearchService) -> None:
    """Verify retrieval of all rental properties in Timóteo."""
    criteria = SearchCriteria.create_rental(city="timoteo")
    results = live_service.search_rentals(criteria)

    assert len(results) >= 10
    first = results[0]
    assert first.identity.property_id != ""
    assert first.price_text != ""


def test_live_property_detail(live_service: HelenaResearchService) -> None:
    """Verify live property detail retrieval for target property."""
    detail = live_service.get_property_detail("4356012")

    assert detail.overview.property_id == "4356012"
    assert detail.overview.reference_code == "636"
    assert detail.pricing.amount == 1200.0
    assert detail.specs.bedrooms == 2
    assert len(detail.photos) >= 4


def test_live_property_photos_ajax(live_service: HelenaResearchService) -> None:
    """Verify live photo retrieval via AJAX endpoint."""
    photos = live_service.get_property_photos("4356012")

    assert len(photos) >= 4
    for url in photos:
        assert url.startswith("https://www.helenaimoveis.com.br/imagens/imoveis/")


def test_live_property_not_found(live_service: HelenaResearchService) -> None:
    """Verify that nonexistent property ID raises PropertyNotFoundError."""
    with pytest.raises(PropertyNotFoundError):
        live_service.get_property_detail("999999999")
