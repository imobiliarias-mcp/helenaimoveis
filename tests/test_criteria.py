"""Unit tests for criteria models and query conversion."""

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
from helena_research.domain.values import AreaRange, PageNumber, PriceRange, RoomCount


def test_location_criteria_single_and_multi() -> None:
    """Test location criteria with city and multi-neighborhood."""
    loc = LocationCriteria(city_slug="timoteo", neighborhood_ids=("660978", "69652"))
    params = loc.query_parameters()
    assert params["bairros"] == "660978,69652"


def test_room_criteria_params() -> None:
    """Test room criteria parameter generation."""
    rc = RoomCriteria(bedrooms=RoomCount(2), suites=RoomCount(1, is_minimum=True))
    params = rc.query_parameters()
    assert params["dormitorios"] == "2"
    assert params["suites"] == "21"


def test_facility_criteria_params() -> None:
    """Test facility criteria parameter generation."""
    fc = FacilityCriteria(bathrooms=RoomCount(1), parking_spaces=RoomCount(2))
    params = fc.query_parameters()
    assert params["banheiros"] == "1"
    assert params["vagas"] == "2"


def test_search_criteria_factory() -> None:
    """Test rental factory method on SearchCriteria."""
    criteria = SearchCriteria.create_rental(
        city="timoteo",
        property_type=PropertyType.APARTAMENTO,
        bedrooms=2,
        min_bedrooms=False,
        max_price=2000,
        page=2,
    )
    assert criteria.scope.transaction == TransactionType.LOCACAO
    assert criteria.scope.property_type == PropertyType.APARTAMENTO
    assert criteria.location.city_slug == "timoteo"
    assert criteria.features.room_criteria.bedrooms == RoomCount(2)
    assert criteria.filters.price_range.maximum == 2000
    assert criteria.page == PageNumber(2)
