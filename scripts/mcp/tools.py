"""Model Context Protocol (MCP) tool adapters for Central Rental Research."""

from typing import Any
from helena_research.application.service import HelenaResearchService
from helena_research.domain.criteria import SearchCriteria


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

    def _format_item(self, item: Any) -> dict[str, Any]:
        """Format individual listing item."""
        pid = getattr(item.property_id, "value", str(item.property_id))
        loc = getattr(item, "location", None)
        neigh = getattr(loc.neighborhood, "value", str(loc.neighborhood)) if loc else ""
        c = getattr(loc.city, "value", str(loc.city)) if loc else ""
        specs = getattr(item, "specs", None)
        beds = getattr(specs.bedrooms, "value", specs.bedrooms) if specs and specs.bedrooms else 0
        baths = getattr(specs.bathrooms, "value", specs.bathrooms) if specs and specs.bathrooms else 0
        url = getattr(item.url, "value", str(item.url)) if hasattr(item, "url") else ""
        return {
            "id": str(pid),
            "title": getattr(item, "title", ""),
            "price": getattr(item, "price_formatted", ""),
            "bedrooms": int(beds) if str(beds).isdigit() else 0,
            "bathrooms": int(baths) if str(baths).isdigit() else 0,
            "neighborhood": neigh,
            "city": c,
            "url": url,
        }

    def get_property_detail(self, property_code: str) -> dict[str, Any]:
        """Retrieve complete property detail for an MCP tool call."""
        detail = self._service.get_property_detail(property_code)
        loc = getattr(detail, "location", None)
        specs = getattr(detail, "specs", None)
        gallery = getattr(detail, "gallery", None)
        photos = getattr(gallery, "urls", []) if gallery else []
        beds = getattr(specs.bedrooms, "value", specs.bedrooms) if specs and specs.bedrooms else 0
        baths = getattr(specs.bathrooms, "value", specs.bathrooms) if specs and specs.bathrooms else 0
        return {
            "id": str(property_code),
            "title": getattr(detail.title, "value", str(detail.title)),
            "description": getattr(detail.description, "value", str(detail.description)),
            "price": getattr(detail, "price_formatted", ""),
            "bedrooms": int(beds) if str(beds).isdigit() else 0,
            "bathrooms": int(baths) if str(baths).isdigit() else 0,
            "neighborhood": getattr(loc.neighborhood, "value", str(loc.neighborhood)) if loc else "",
            "city": getattr(loc.city, "value", str(loc.city)) if loc else "",
            "url": getattr(detail.url, "value", str(detail.url)) if hasattr(detail, "url") else "",
            "photos": list(photos),
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
