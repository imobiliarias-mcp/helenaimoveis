"""Unit tests for property detail HTML parser."""

from pathlib import Path
import pytest
from helena_research.domain.exceptions import PropertyNotFoundError
from helena_research.parsers.detail_parser import DetailParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_property_detail() -> None:
    """Test parsing complete property detail from fixture."""
    html_path = FIXTURES_DIR / "detail_4356012.html"
    content = html_path.read_text(encoding="iso-8859-1")
    parser = DetailParser()
    detail = parser.parse(content, "4356012", "https://www.helenaimoveis.com.br/imovel/4356012")

    assert detail.overview.property_id == "4356012"
    assert detail.overview.reference_code == "636"
    assert "APARTAMENTO COM 02 QUARTOS" in detail.overview.description

    assert detail.pricing.amount == 1200.0
    assert detail.pricing.iptu == 53.0
    assert detail.pricing.currency == "BRL"

    assert detail.location.city == "Timóteo"
    assert detail.location.neighborhood == "Centro Norte"
    assert "Rua 08 de Novembro" in detail.location.address

    assert detail.specs.bedrooms == 2
    assert detail.specs.bathrooms == 1
    assert detail.specs.parking_spaces == 1

    assert "Móveis Planejados" in detail.characteristics
    assert "Cozinha" in detail.characteristics

    assert len(detail.photos) == 6
    assert detail.photos.first_photo() is not None


def test_redirect_home_raises_not_found() -> None:
    """Test that redirection to home triggers PropertyNotFoundError."""
    parser = DetailParser()
    with pytest.raises(PropertyNotFoundError):
        parser.parse("<html><body>Redirected</body></html>", "99999", "https://www.helenaimoveis.com.br/")
