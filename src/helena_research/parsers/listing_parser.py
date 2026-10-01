"""Parser for extracting property listings from HTML search results."""

import re
from bs4 import BeautifulSoup, Tag
from helena_research.domain.listing import (
    ListingCollection,
    ListingIdentity,
    ListingLocation,
    ListingSpecs,
    ListingSummary,
)


class ListingParser:
    """Parses search result pages into typed ListingCollection entities."""

    def parse(self, html_content: str, current_page: int = 1) -> ListingCollection:
        """Parse raw HTML and return a domain listing collection."""
        soup = BeautifulSoup(html_content, "html.parser")
        card_tags = soup.find_all("div", class_="imovelcard")
        items = tuple(self._parse_card(t) for t in card_tags if t.get("data-link"))
        has_next = self._detect_has_next(soup)
        return ListingCollection(
            items=items, current_page=current_page, has_next_page=has_next
        )

    def _parse_card(self, tag: Tag) -> ListingSummary:
        """Transform a single HTML card tag into ListingSummary."""
        link = str(tag.get("data-link", ""))
        prop_id = self._extract_id_from_link(link)
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
        )

    def _extract_id_from_link(self, link: str) -> str:
        """Extract numeric property identifier from link path."""
        match = re.search(r"/imovel/(\d+)", link)
        if match:
            return match.group(1)
        return ""

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
