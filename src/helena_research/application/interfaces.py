"""Application ports and contracts for central rental research MCP integration."""

from typing import Protocol
from helena_research.domain.criteria import SearchCriteria
from helena_research.domain.listing import ListingCollection
from helena_research.domain.property import PhotoGallery, PropertyDetail


class RentalSearchPort(Protocol):
    """Primary port for executing rental search queries."""

    def search_rentals(self, criteria: SearchCriteria) -> ListingCollection:
        """Execute rental search according to domain criteria."""
        ...


class PropertyDetailPort(Protocol):
    """Port for retrieving rich property detail views."""

    def get_property_detail(self, property_id: str) -> PropertyDetail:
        """Retrieve full property detail by identifier."""
        ...


class PropertyMediaPort(Protocol):
    """Port for retrieving full photo gallery assets."""

    def get_property_photos(self, property_id: str) -> PhotoGallery:
        """Retrieve photo gallery collection for a property."""
        ...
