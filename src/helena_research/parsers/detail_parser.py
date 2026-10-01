"""Parser for extracting complete property details from HTML."""

import json
import re
from bs4 import BeautifulSoup, Tag
from helena_research.domain.exceptions import PropertyNotFoundError
from helena_research.domain.property import (
    PhotoGallery,
    PropertyDetail,
    PropertyLocation,
    PropertyOverview,
    PropertyPricing,
    PropertySpecs,
)


class DetailParser:
    """Parses property detail HTML and structured JSON-LD into PropertyDetail."""

    def parse(self, html_content: str, property_id: str, final_url: str = "") -> PropertyDetail:
        """Parse raw HTML and return a PropertyDetail entity."""
        soup = BeautifulSoup(html_content, "html.parser")
        self._validate_not_redirected(soup, property_id, final_url)
        json_rent, json_product = self._extract_json_ld(soup)
        overview = self._parse_overview(soup, property_id, json_product)
        pricing = self._parse_pricing(soup, json_rent)
        location = self._parse_location(soup, json_rent)
        specs = self._parse_specs(soup)
        characteristics = self._parse_characteristics(soup)
        photos = self._parse_photos(soup)
        return PropertyDetail(
            overview=overview,
            pricing=pricing,
            location=location,
            specs=specs,
            characteristics=characteristics,
            photos=photos,
            canonical_url=final_url,
        )

    def _validate_not_redirected(self, soup: BeautifulSoup, property_id: str, final_url: str) -> None:
        """Raise PropertyNotFoundError if redirected to home or not found."""
        if final_url.rstrip("/").endswith("helenaimoveis.com.br"):
            raise PropertyNotFoundError(f"Property {property_id} was not found (redirected to home)")
        if not soup.find(id="desc_descricao") and not soup.find(class_="imovelcard"):
            if not soup.find("div", class_="descricao"):
                raise PropertyNotFoundError(f"Property {property_id} not found in portal")

    def _extract_json_ld(self, soup: BeautifulSoup) -> tuple[dict, dict]:
        """Extract RentAction and Product schemas from JSON-LD tags."""
        rent_data: dict = {}
        prod_data: dict = {}
        for script in soup.find_all("script", type="application/ld+json"):
            self._fill_json_dict(script, rent_data, prod_data)
        return (rent_data, prod_data)

    def _fill_json_dict(self, script: Tag, rent_data: dict, prod_data: dict) -> None:
        """Helper to parse a single JSON-LD script."""
        try:
            parsed = json.loads(script.string or "")
            t = parsed.get("@type")
            if t == "RentAction":
                rent_data.update(parsed)
            if t == "Product":
                prod_data.update(parsed)
        except (json.JSONDecodeError, AttributeError):
            return

    def _parse_overview(self, soup: BeautifulSoup, prop_id: str, prod: dict) -> PropertyOverview:
        """Extract title, reference code, and text description."""
        title = str(prod.get("name") or (soup.title.string.strip() if soup.title else ""))
        ref_code = self._extract_ref_code(soup)
        desc = self._extract_description(soup)
        return PropertyOverview(property_id=prop_id, title=title, reference_code=ref_code, description=desc)

    def _extract_ref_code(self, soup: BeautifulSoup) -> str:
        """Extract internal reference code from text elements."""
        for tag in soup.find_all(lambda t: t.name in ["p", "span", "div"] and "Ref:" in t.get_text()):
            match = re.search(r"Ref:\s*(\w+)", tag.get_text())
            if match:
                return match.group(1)
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract textual property description."""
        desc_el = soup.find(id="desc_descricao")
        if not desc_el:
            return ""
        p_tag = desc_el.find("p")
        if p_tag:
            return p_tag.get_text("\n", strip=True)
        return desc_el.get_text("\n", strip=True)

    def _parse_pricing(self, soup: BeautifulSoup, rent_ld: dict) -> PropertyPricing:
        """Extract amount, condomínio, and IPTU."""
        amount = self._extract_amount(rent_ld, soup)
        condo = self._extract_fee(soup, "Condomínio")
        iptu = self._extract_fee(soup, "IPTU")
        fmt = f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if amount else ""
        return PropertyPricing(amount=amount, condo_fee=condo, iptu=iptu, formatted_text=fmt)

    def _extract_amount(self, rent_ld: dict, soup: BeautifulSoup) -> float | None:
        """Extract base rental amount."""
        raw_price = rent_ld.get("price")
        if raw_price:
            try:
                return float(str(raw_price).replace(",", "."))
            except ValueError:
                pass
        for val_tag in soup.find_all(class_="imovelcard__valor__valor"):
            txt = val_tag.get_text(strip=True)
            num = re.sub(r"[^\d]", "", txt)
            if num:
                return float(num)
        return None

    def _extract_fee(self, soup: BeautifulSoup, fee_name: str) -> float | None:
        """Extract numerical fee for condomínio or IPTU."""
        for tag in soup.find_all(class_="info__tag"):
            txt = tag.get_text(" ", strip=True)
            if fee_name in txt:
                clean = re.sub(r"[^\d,]", "", txt)
                try:
                    return float(clean.replace(".", "").replace(",", "."))
                except ValueError:
                    return None
        return None

    def _parse_location(self, soup: BeautifulSoup, rent_ld: dict) -> PropertyLocation:
        """Extract geographic location attributes."""
        addr_ld = rent_ld.get("object", {}).get("address", {})
        street = str(addr_ld.get("streetAddress", ""))
        city = str(addr_ld.get("addressLocality", "Timóteo"))
        state = str(addr_ld.get("addressRegion", "MG"))
        neighborhood = self._extract_neighborhood_from_title(soup)
        return PropertyLocation(address=street, neighborhood=neighborhood, city=city, state=state)

    def _extract_neighborhood_from_title(self, soup: BeautifulSoup) -> str:
        """Extract neighborhood from title or header tags."""
        text = soup.title.string if soup.title else ""
        match = re.search(r"bairro\s+([^,]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _parse_specs(self, soup: BeautifulSoup) -> PropertySpecs:
        """Extract room and garage specifications."""
        data: dict[str, int | str] = {}
        for tag in soup.find_all(class_="info__tag"):
            self._fill_spec(tag.get_text(" ", strip=True), data)
        return PropertySpecs(
            bedrooms=int(data["bedrooms"]) if "bedrooms" in data else None,
            suites=int(data["suites"]) if "suites" in data else None,
            bathrooms=int(data["bathrooms"]) if "bathrooms" in data else None,
            parking_spaces=int(data["parking"]) if "parking" in data else None,
            usable_area=str(data["area"]) if "area" in data else None,
        )

    def _fill_spec(self, text: str, data: dict[str, int | str]) -> None:
        """Inspect tag text and populate spec count."""
        match = re.search(r"\d+", text)
        val = int(match.group(0)) if match else 0
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

    def _parse_characteristics(self, soup: BeautifulSoup) -> tuple[str, ...]:
        """Extract list of amenities and characteristics."""
        items: list[str] = []
        for cx in soup.find_all(class_="cxItem"):
            txt = cx.get_text(" ", strip=True)
            if txt and txt not in items:
                items.append(txt)
        return tuple(items)

    def _parse_photos(self, soup: BeautifulSoup) -> PhotoGallery:
        """Extract photo URLs from image slider."""
        gal = soup.find(id="galeria-inicial")
        if not gal:
            return PhotoGallery()
        urls: list[str] = []
        for img in gal.find_all("img"):
            src = img.get("src")
            if src and src not in urls:
                urls.append(str(src))
        return PhotoGallery(photo_urls=tuple(urls))
