"""Model Context Protocol (MCP) tool adapters for Central Rental Research."""

from typing import Any
from helena_research.application.service import HelenaResearchService
from helena_research.domain.criteria import SearchCriteria
from helena_research.domain.listing import ListingSummary
from helena_research.domain.property import PropertyDetail


class HelenaMcpAdapter:
    """Adapts Helena rental service for consumption by MCP servers and tool registries."""

    def __init__(self, service: Any = None) -> None:
        """Initialize adapter with an abstract rental service."""
        self._service = service or HelenaResearchService()

    @classmethod
    def create_default(cls) -> "HelenaMcpAdapter":
        """Factory constructor instantiating default Helena provider."""
        return cls()

    def _build_criteria(self, city: str, max_price: float, bedrooms: int, page: int) -> SearchCriteria:
        """Build domain SearchCriteria from tool parameters."""
        c = city.lower() if city else "timoteo"
        b = bedrooms if bedrooms > 0 else None
        p = int(max_price) if max_price > 0 else None
        return SearchCriteria.create_rental(
            city=c,
            bedrooms=b,
            max_price=p,
            page=page,
        )

    def search_rentals(
        self,
        city: str = "Timóteo",
        min_price: float = 0.0,
        max_price: float = 0.0,
        bedrooms: int = 0,
        property_type: str = "",
        page: int = 1,
    ) -> dict[str, Any]:
        """Execute a rental property search for an MCP tool call."""
        criteria = self._build_criteria(city, max_price, bedrooms, page)
        results = self._service.search_rentals(criteria)
        return self._format_collection(results)

    def _format_collection(self, collection: Any) -> dict[str, Any]:
        """Format listing collection into standard dictionary."""
        return {
            "provider": "helenaimoveis",
            "total_count": len(collection),
            "listings": [self._format_item(item) for item in collection],
        }

    def _format_item(self, item: ListingSummary) -> dict[str, Any]:
        """Format a ListingSummary into the standard listing dictionary."""
        return {
            "id": item.identity.property_id,
            "title": item.title,
            "price": item.price_text,
            "bedrooms": item.specs.bedrooms or 0,
            "bathrooms": item.specs.bathrooms or 0,
            "neighborhood": item.location.neighborhood,
            "city": item.location.city,
            "url": item.url,
            "media_url": item.thumbnail_url or "",
        }

    def get_property_detail(self, property_code: str) -> dict[str, Any]:
        """Retrieve complete property detail for an MCP tool call."""
        detail: PropertyDetail = self._service.get_property_detail(property_code)
        overview = detail.overview
        pricing = detail.pricing
        location = detail.location
        specs = detail.specs
        return {
            "id": str(property_code),
            "title": overview.title,
            "description": overview.description,
            "price": pricing.formatted_text,
            "condo_fee": pricing.condo_fee,
            "iptu": pricing.iptu,
            "bedrooms": specs.bedrooms or 0,
            "bathrooms": specs.bathrooms or 0,
            "neighborhood": location.neighborhood,
            "city": location.city,
            "url": detail.canonical_url,
            "photos": list(detail.photos.photo_urls),
        }

    def get_facets(self) -> dict[str, Any]:
        """Retrieve available search facets for an MCP tool call."""
        return {"cities": [{"name": "Timóteo"}, {"name": "Coronel Fabriciano"}, {"name": "Ipatinga"}]}

    def get_provider_info(self) -> dict[str, Any]:
        """Retrieve metadata about this rental provider adapter."""
        return {
            "provider_name": "helenaimoveis",
            "coverage_region": "Timóteo, Coronel Fabriciano, Ipatinga",
            "supported_operations": ["search_rentals", "get_property_detail", "get_facets"],
        }
