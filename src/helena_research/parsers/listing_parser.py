"""Parser for extracting property listings from HTML search results."""

import re
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup, Tag

from helena_research.domain.exceptions import InvalidPublicPropertyUrlError
from helena_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingLocation,
    ListingSpecs,
    ListingSummary,
)


class ListingParser:
    """Parses search result pages into typed ListingCollection entities."""

    def __init__(
        self, public_base_url: str = "https://www.helenaimoveis.com.br"
    ) -> None:
        """Configure the public site origin used to resolve card URLs."""
        self._public_base_url = public_base_url.rstrip("/")
        self._validate_public_base()

    def parse(self, html_content: str, current_page: int = 1) -> ListingCollection:
        """Parse raw HTML and return a domain listing collection."""
        soup = BeautifulSoup(html_content, "html.parser")
        card_tags = soup.find_all("div", class_="imovelcard")
        items = tuple(self._parse_card(tag) for tag in card_tags if self._is_listing_card(tag))
        has_next = self._detect_has_next(soup)
        return ListingCollection(
            items=items, current_page=current_page, has_next_page=has_next
        )

    def _parse_card(self, tag: Tag) -> ListingSummary:
        """Transform a single HTML card tag into ListingSummary."""
        link = self._extract_card_link(tag)
        prop_id = self._extract_id_from_link(link)
        public_url = self._resolve_public_url(link, prop_id)
        identity = ListingIdentity(property_id=prop_id, url_path=link)
        title, thumb = self._extract_title_and_thumb(tag)
        location = self._extract_location(tag)
        price_text = self._extract_price(tag)
        specs = self._extract_specs(tag)
        ref_code = self._extract_ref(tag)
        return ListingSummary(
            identity=identity,
            title=title,
            location=location,
            price_text=price_text,
            specs=specs,
            reference_code=ref_code,
            thumbnail_url=thumb,
            url=public_url,
        )

    def _extract_card_link(self, tag: Tag) -> str:
        """Return canonical card path or a real detail anchor href."""
        link = str(tag.get("data-link", "")).strip()
        if link:
            return link
        anchor = tag.select_one(".imovelcard__img")
        if anchor and anchor.get("href"):
            return str(anchor.get("href"))
        raise InvalidPublicPropertyUrlError("Listing card has no recoverable public URL.")

    def _extract_id_from_link(self, link: str) -> str:
        """Extract numeric property identifier from link path."""
        try:
            path = urlsplit(link).path
        except ValueError as error:
            raise InvalidPublicPropertyUrlError(
                f"Listing card has malformed public URL '{link}'."
            ) from error
        match = re.search(r"/imovel/(\d+)", path)
        if match:
            return match.group(1)
        return ""

    def _is_listing_card(self, tag: Tag) -> bool:
        """Include result cards and skip pagination-only wrappers."""
        return bool(tag.get("data-link") or tag.find(class_="imovelcard__info"))

    def _validate_public_base(self) -> None:
        """Reject invalid public URL configuration before parsing."""
        base = urlsplit(self._public_base_url)
        if base.scheme not in {"http", "https"} or not base.hostname:
            raise InvalidPublicPropertyUrlError(
                f"Invalid public property URL base '{self._public_base_url}'."
            )

    def _resolve_public_url(self, link: str, property_id: str) -> str:
        """Resolve and validate a property's public page URL."""
        target = urljoin(f"{self._public_base_url}/", link)
        parsed_target = urlsplit(target)
        self._validate_public_target(parsed_target, property_id, link)
        return target

    def _validate_public_target(self, target, property_id: str, link: str) -> None:
        """Reject non-web, cross-site, or non-property URL targets."""
        host_matches = self._same_host(target.hostname)
        segments = [part for part in target.path.split("/") if part]
        is_property = len(segments) > 1 and segments[0] == "imovel" and segments[1].isdigit()
        if target.scheme not in {"http", "https"} or not target.hostname or not host_matches or not is_property:
            raise InvalidPublicPropertyUrlError(
                f"Property '{property_id}' has invalid public URL '{link}'."
            )

    def _same_host(self, hostname: str | None) -> bool:
        """Compare configured and destination portal hosts."""
        base_hostname = urlsplit(self._public_base_url).hostname or ""
        target_hostname = hostname or ""
        return base_hostname.lower().removeprefix("www.") == target_hostname.lower().removeprefix("www.")

    def _extract_title_and_thumb(self, tag: Tag) -> tuple[str, str | None]:
        """Extract property title and thumbnail URL from image element."""
        img = tag.find("img")
        if not img:
            return ("", None)
        title = str(img.get("alt", "") or img.get("title", ""))
        thumb = img.get("src")
        return (title, str(thumb) if thumb else None)

    def _extract_location(self, tag: Tag) -> ListingLocation:
        """Extract neighborhood, city, and state."""
        loc_el = tag.find(class_="imovelcard__info__local")
        if not loc_el:
            return ListingLocation(neighborhood="", city="")
        text = loc_el.get_text(strip=True)
        parts = [p.strip() for p in text.split(",")]
        bairro = parts[0] if parts else ""
        city_raw = parts[1] if len(parts) > 1 else ""
        city_parts = [c.strip() for c in city_raw.split("/")]
        city = city_parts[0] if city_parts else ""
        state = city_parts[1] if len(city_parts) > 1 else "MG"
        return ListingLocation(neighborhood=bairro, city=city, state=state)

    def _extract_price(self, tag: Tag) -> str:
        """Extract formatted price string from card."""
        price_el = tag.find(class_="imovelcard__valor__valor")
        if not price_el:
            return ""
        return price_el.get_text(strip=True)

    def _extract_ref(self, tag: Tag) -> str | None:
        """Extract internal reference code from card."""
        ref_el = tag.find(class_="imovelcard__info__ref")
        if not ref_el:
            return None
        text = ref_el.get_text(strip=True)
        match = re.search(r"Ref:\s*(\w+)", text)
        if match:
            return match.group(1)
        return None

    def _extract_specs(self, tag: Tag) -> ListingSpecs:
        """Extract numerical specs (dormitórios, banheiros, vagas, área)."""
        data: dict[str, int | str] = {}
        for feat in tag.find_all(class_="imovelcard__info__feature"):
            self._fill_spec_item(feat.get_text(" ", strip=True), data)
        return ListingSpecs(
            bedrooms=int(data["bedrooms"]) if "bedrooms" in data else None,
            suites=int(data["suites"]) if "suites" in data else None,
            bathrooms=int(data["bathrooms"]) if "bathrooms" in data else None,
            parking_spaces=int(data["parking"]) if "parking" in data else None,
            area_text=str(data["area"]) if "area" in data else None,
        )

    def _fill_spec_item(self, text: str, data: dict[str, int | str]) -> None:
        """Inspect feature text and populate data dict."""
        number_match = re.search(r"\d+", text)
        val = int(number_match.group(0)) if number_match else 0
        if "Dormit" in text or "Quarto" in text:
            data["bedrooms"] = val
            return
        if "Suíte" in text:
            data["suites"] = val
            return
        if "Banheiro" in text:
            data["bathrooms"] = val
            return
        if "Vaga" in text or "Garagem" in text:
            data["parking"] = val
            return
        if "m²" in text:
            data["area"] = text

    def _detect_has_next(self, soup: BeautifulSoup) -> bool:
        """Detect whether a subsequent page link exists in pagination."""
        pag = soup.find(class_="lista_imoveis_paginacao")
        if not pag:
            return False
        for link in pag.find_all("a"):
            text = link.get_text(strip=True)
            if ">" in text or "próxima" in text.lower():
                return True
        return False
