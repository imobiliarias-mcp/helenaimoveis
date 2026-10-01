"""Domain layer exports for Helena Imóveis rental research."""

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
from helena_research.domain.exceptions import (
    HelenaResearchError,
    InvalidCriteriaError,
    ParsingError,
    PortalConnectionError,
    PropertyNotFoundError,
)
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
from helena_research.domain.values import AreaRange, PageNumber, PriceRange, RoomCount

__all__ = [
    "AreaRange",
    "FacilityCriteria",
    "FeatureBundle",
    "FilterBundle",
    "HelenaResearchError",
    "InvalidCriteriaError",
    "ListingCollection",
    "ListingIdentity",
    "ListingLocation",
    "ListingSpecs",
    "ListingSummary",
    "LocationCriteria",
    "PageNumber",
    "ParsingError",
    "PhotoGallery",
    "PortalConnectionError",
    "PriceRange",
    "PropertyDetail",
    "PropertyLocation",
    "PropertyNotFoundError",
    "PropertyOverview",
    "PropertyPricing",
    "PropertySpecs",
    "PropertyType",
    "RoomCount",
    "RoomCriteria",
    "SearchCriteria",
    "SearchScope",
    "SortOrder",
    "TransactionType",
]
