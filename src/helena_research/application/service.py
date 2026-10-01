"""Service facade orchestrating transport and parsing for Helena Imóveis."""

from helena_research.domain.criteria import SearchCriteria
from helena_research.domain.listing import ListingCollection
from helena_research.domain.property import PhotoGallery, PropertyDetail
from helena_research.infrastructure.http_client import (
    HttpClientProtocol,
    HttpResponse,
    HttpxHttpClient,
)
from helena_research.infrastructure.url_builder import UrlBuilder
from helena_research.parsers.detail_parser import DetailParser
from helena_research.parsers.listing_parser import ListingParser
from helena_research.parsers.photo_parser import PhotoParser


class TransportCoordinator:
    """Coordinating component managing HTTP client and URL creation."""

    def __init__(
        self,
        http_client: HttpClientProtocol | None = None,
        url_builder: UrlBuilder | None = None,
    ) -> None:
        """Initialize transport coordinator with client and URL builder."""
        self._http = http_client or HttpxHttpClient()
        self._urls = url_builder or UrlBuilder()

    def fetch_search(self, criteria: SearchCriteria) -> HttpResponse:
        """Construct search URL and fetch response."""
        url = self._urls.build_search_url(criteria)
        return self._http.get(url)

    def fetch_detail(self, property_id: str) -> HttpResponse:
        """Construct detail URL and fetch response."""
        url = self._urls.build_detail_url(property_id)
        return self._http.get(url)

    def fetch_photos(self, property_id: str) -> HttpResponse:
        """Construct AJAX photo gallery URL and fetch response."""
        url = self._urls.build_photos_url(property_id)
        return self._http.get(url)

    def fetch_raw_url(self, url: str) -> HttpResponse:
        """Fetch arbitrary URL."""
        return self._http.get(url)


class ParserCoordinator:
    """Coordinating component managing domain parsers."""

    def __init__(
        self,
        listing_parser: ListingParser | None = None,
        detail_parser: DetailParser | None = None,
        photo_parser: PhotoParser | None = None,
    ) -> None:
        """Initialize parser coordinator with parsing engines."""
        self._listing = listing_parser or ListingParser()
        self._detail = detail_parser or DetailParser()
        self._photo = photo_parser or PhotoParser()

    def parse_listing(self, html: str, page: int = 1) -> ListingCollection:
        """Parse search listing HTML."""
        return self._listing.parse(html, current_page=page)

    def parse_detail(self, html: str, property_id: str, final_url: str) -> PropertyDetail:
        """Parse property detail HTML."""
        return self._detail.parse(html, property_id=property_id, final_url=final_url)

    def parse_photos(self, json_content: str) -> PhotoGallery:
        """Parse AJAX photo JSON response."""
        return self._photo.parse(json_content)


class HelenaResearchService:
    """Primary facade for Helena Imóveis rental research implementing MCP contracts."""

    def __init__(
        self,
        transport: TransportCoordinator | None = None,
        parsers: ParserCoordinator | None = None,
    ) -> None:
        """Initialize service with coordinators complying with 2-field rule."""
        self._transport = transport or TransportCoordinator()
        self._parsers = parsers or ParserCoordinator()

    def search_rentals(self, criteria: SearchCriteria) -> ListingCollection:
        """Execute rental search according to domain specification."""
        response = self._transport.fetch_search(criteria)
        return self._parsers.parse_listing(response.text, page=criteria.page.value)

    def search_by_url(self, target_url: str, page: int = 1) -> ListingCollection:
        """Execute rental search directly from a target portal URL."""
        response = self._transport.fetch_raw_url(target_url)
        return self._parsers.parse_listing(response.text, page=page)

    def get_property_detail(self, property_id: str) -> PropertyDetail:
        """Retrieve full property details and specifications."""
        response = self._transport.fetch_detail(property_id)
        return self._parsers.parse_detail(
            response.text, property_id=property_id, final_url=response.final_url
        )

    def get_property_photos(self, property_id: str) -> PhotoGallery:
        """Retrieve full photo gallery via AJAX media endpoint."""
        response = self._transport.fetch_photos(property_id)
        return self._parsers.parse_photos(response.text)
