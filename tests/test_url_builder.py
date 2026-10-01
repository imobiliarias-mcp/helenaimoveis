"""Unit tests for URL construction."""

from helena_research.domain.criteria import (
    FacilityCriteria,
    FeatureBundle,
    FilterBundle,
    LocationCriteria,
    RoomCriteria,
    SearchCriteria,
    SearchScope,
)
from helena_research.domain.enums import PropertyType, SortOrder, TransactionType
from helena_research.domain.values import PageNumber, PriceRange, RoomCount
from helena_research.infrastructure.url_builder import UrlBuilder


def test_target_prompt_url_construction() -> None:
    """Verify exact target URL from prompt matches builder output."""
    builder = UrlBuilder()
    criteria = SearchCriteria.create_rental(
        city="timoteo",
        property_type=PropertyType.TODOS,
        bedrooms=2,
        min_bedrooms=False,
    )
    url = builder.build_search_url(criteria)
    expected = "https://www.helenaimoveis.com.br/imovel/locacao/todos/timoteo/?&dormitorios=2"
    assert url == expected


def test_search_url_with_all_filters() -> None:
    """Verify search URL with price, sorting, and pagination."""
    builder = UrlBuilder()
    criteria = SearchCriteria(
        scope=SearchScope(TransactionType.LOCACAO, PropertyType.APARTAMENTO),
        location=LocationCriteria(city_slug="timoteo", neighborhood_ids=("660978",)),
        filters=FilterBundle(price_range=PriceRange(minimum=1000, maximum=2500)),
        features=FeatureBundle(room_criteria=RoomCriteria(bedrooms=RoomCount(2, is_minimum=True))),
        sort_order=SortOrder.MENOR_VALOR,
        page=PageNumber(2),
    )
    url = builder.build_search_url(criteria)
    assert "https://www.helenaimoveis.com.br/imovel/locacao/apartamento/timoteo/?&" in url
    assert "vmi=1000" in url
    assert "vma=2500" in url
    assert "dormitorios=22" in url
    assert "bairros=660978" in url
    assert "ord=menor_valor" in url
    assert "pag=2" in url


def test_detail_and_photos_url() -> None:
    """Verify detail and AJAX photo endpoint generation."""
    builder = UrlBuilder()
    detail_url = builder.build_detail_url("4356012")
    assert detail_url == "https://www.helenaimoveis.com.br/imovel/4356012"

    photos_url = builder.build_photos_url("4356012")
    assert photos_url == "https://www.helenaimoveis.com.br/t27/lista_imoveis_fotos.php?imovel=4356012"
