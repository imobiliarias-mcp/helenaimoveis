"""Contract tests for HelenaMcpAdapter.

The fake service returns the production domain dataclasses (ListingSummary,
PropertyDetail and friends), so any drift in field names or shape breaks here.
"""

from helena_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingLocation,
    ListingSpecs,
    ListingSummary,
)
from helena_research.domain.property import (
    PhotoGallery,
    PropertyDetail,
    PropertyLocation,
    PropertyOverview,
    PropertyPricing,
    PropertySpecs,
)
from scripts.mcp.tools import HelenaMcpAdapter

PROPERTY_ID = "999"
PROPERTY_URL = "https://www.helenaimoveis.com.br/imovel/999"
THUMBNAIL_URL = "https://www.helenaimoveis.com.br/thumb.jpg"
PHOTO_URL = "https://www.helenaimoveis.com.br/foto1.jpg"


def _listing() -> ListingSummary:
    """Build a real ListingSummary as the parser would."""
    return ListingSummary(
        identity=ListingIdentity(property_id=PROPERTY_ID, url_path="/imovel/999"),
        title="Apto Centro Timóteo",
        location=ListingLocation(neighborhood="Centro", city="Timóteo"),
        price_text="R$ 1.100,00",
        specs=ListingSpecs(bedrooms=2, bathrooms=1),
        thumbnail_url=THUMBNAIL_URL,
        url=PROPERTY_URL,
    )


def _detail() -> PropertyDetail:
    """Build a real PropertyDetail as the detail parser would."""
    return PropertyDetail(
        overview=PropertyOverview(
            property_id=PROPERTY_ID,
            title="Apto Centro Timóteo",
            reference_code="REF-1",
            description="Ótimo apartamento",
        ),
        pricing=PropertyPricing(
            amount=1100.0,
            condo_fee=200.0,
            iptu=50.0,
            formatted_text="R$ 1.100,00",
        ),
        location=PropertyLocation(address="Rua A", neighborhood="Centro", city="Timóteo"),
        specs=PropertySpecs(bedrooms=2, bathrooms=1, parking_spaces=1, usable_area="75"),
        photos=PhotoGallery(photo_urls=(PHOTO_URL,)),
        canonical_url=PROPERTY_URL,
    )


class FakeService:
    """Service double returning real domain objects."""

    def search_rentals(self, criteria):
        """Return a one-item listing collection."""
        return ListingCollection(items=(_listing(),), current_page=1)

    def get_property_detail(self, property_id):
        """Return the detail for the requested property."""
        assert property_id == PROPERTY_ID
        return _detail()


def _adapter() -> HelenaMcpAdapter:
    """Build the adapter wired to the domain-typed fake service."""
    return HelenaMcpAdapter(service=FakeService())


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    info = _adapter().get_provider_info()
    assert info["provider_name"] == "helenaimoveis"
    assert "search_rentals" in info["supported_operations"]


def test_search_rentals_maps_real_listing_fields():
    """Search must read identity, price_text and thumbnail from the real model."""
    res = _adapter().search_rentals(city="Timóteo", bedrooms=2, max_price=1500.0)
    assert res["provider"] == "helenaimoveis"
    assert res["total_count"] == 1
    listing = res["listings"][0]
    assert listing["id"] == PROPERTY_ID
    assert listing["title"] == "Apto Centro Timóteo"
    assert listing["price"] == "R$ 1.100,00"
    assert listing["bedrooms"] == 2
    assert listing["bathrooms"] == 1
    assert listing["neighborhood"] == "Centro"
    assert listing["city"] == "Timóteo"
    assert listing["url"] == PROPERTY_URL
    assert listing["media_url"] == THUMBNAIL_URL


def test_property_detail_maps_real_overview_pricing_and_photos():
    """Detail must read overview, pricing, location, specs and photo gallery."""
    detail = _adapter().get_property_detail(PROPERTY_ID)
    assert isinstance(detail, dict)
    assert detail["id"] == PROPERTY_ID
    assert detail["title"] == "Apto Centro Timóteo"
    assert detail["description"] == "Ótimo apartamento"
    assert detail["price"] == "R$ 1.100,00"
    assert detail["condo_fee"] == 200.0
    assert detail["iptu"] == 50.0
    assert detail["bedrooms"] == 2
    assert detail["bathrooms"] == 1
    assert detail["neighborhood"] == "Centro"
    assert detail["city"] == "Timóteo"
    assert detail["url"] == PROPERTY_URL
    assert detail["photos"] == [PHOTO_URL]
