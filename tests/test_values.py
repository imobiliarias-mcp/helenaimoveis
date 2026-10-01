"""Unit tests for domain value objects."""

import pytest
from helena_research.domain.exceptions import InvalidCriteriaError
from helena_research.domain.values import AreaRange, PageNumber, PriceRange, RoomCount


def test_price_range_valid() -> None:
    """Test valid price range query conversion."""
    pr = PriceRange(minimum=1000, maximum=3000)
    params = pr.query_parameters()
    assert params["vmi"] == "1000"
    assert params["vma"] == "3000"


def test_price_range_invalid() -> None:
    """Test invalid price range raises exception."""
    with pytest.raises(InvalidCriteriaError):
        PriceRange(minimum=5000, maximum=1000)
    with pytest.raises(InvalidCriteriaError):
        PriceRange(minimum=-10)


def test_area_range_valid() -> None:
    """Test valid area range query conversion."""
    ar = AreaRange(minimum=50, maximum=120)
    params = ar.query_parameters()
    assert params["areaMinima"] == "50"
    assert params["areaMaxima"] == "120"


def test_area_range_invalid() -> None:
    """Test invalid area range raises exception."""
    with pytest.raises(InvalidCriteriaError):
        AreaRange(minimum=200, maximum=100)


def test_room_count_exact() -> None:
    """Test exact room count param code."""
    rc = RoomCount(count=2, is_minimum=False)
    assert rc.to_param_code() == "2"


def test_room_count_minimum() -> None:
    """Test 'N or more' room count param code."""
    rc = RoomCount(count=2, is_minimum=True)
    assert rc.to_param_code() == "22"


def test_room_count_bounds() -> None:
    """Test room count boundaries (1 to 5)."""
    with pytest.raises(InvalidCriteriaError):
        RoomCount(count=0)
    with pytest.raises(InvalidCriteriaError):
        RoomCount(count=6)


def test_page_number_valid() -> None:
    """Test valid page number."""
    p = PageNumber(value=3)
    assert p.to_param_code() == "3"


def test_page_number_invalid() -> None:
    """Test non-positive page number."""
    with pytest.raises(InvalidCriteriaError):
        PageNumber(value=0)
