"""Unit tests for HelenaMcpAdapter."""

from scripts.mcp.tools import HelenaMcpAdapter


class DummyService:
    """Dummy service for testing Helena MCP adapter."""

    def search_rentals(self, criteria):
        class DummyListing:
            property_id = type("Id", (), {"value": "999"})()
            title = "Apto Centro Timóteo"
            price = type("Price", (), {"value": 1100.0})()
            price_formatted = "R$ 1.100,00"
            specs = type("Specs", (), {"bedrooms": type("B", (), {"value": 2})(), "bathrooms": type("B", (), {"value": 1})()})()
            location = type("Loc", (), {"neighborhood": type("N", (), {"value": "Centro"})(), "city": type("C", (), {"value": "Timóteo"})()})()
            url = type("Url", (), {"value": "https://www.helenaimoveis.com.br/imovel/999"})()
        class DummyCollection(list):
            total_count = 1
        return DummyCollection([DummyListing()])

    def get_property_detail(self, property_id):
        p_id = property_id
        class DummyDetail:
            property_id = type("Id", (), {"value": p_id})()
            title = type("T", (), {"value": "Apto Centro Timóteo"})()
            description = type("D", (), {"value": "Ótimo apartamento"})()
            price = type("P", (), {"value": 1100.0})()
            price_formatted = "R$ 1.100,00"
            specs = type("Specs", (), {"bedrooms": type("B", (), {"value": 2})(), "bathrooms": type("B", (), {"value": 1})(), "parking_spaces": type("P", (), {"value": 1})(), "usable_area": type("A", (), {"value": 75.0})()})()
            location = type("Loc", (), {"neighborhood": type("N", (), {"value": "Centro"})(), "city": type("C", (), {"value": "Timóteo"})(), "state": type("S", (), {"value": "MG"})()})()
            url = type("Url", (), {"value": f"https://www.helenaimoveis.com.br/imovel/{p_id}"})()
            gallery = type("G", (), {"urls": ["https://www.helenaimoveis.com.br/foto1.jpg"]})()
        return DummyDetail()

    def get_property_photos(self, property_id):
        return type("G", (), {"urls": ["https://www.helenaimoveis.com.br/foto1.jpg"]})()


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    adapter = HelenaMcpAdapter(service=DummyService())
    info = adapter.get_provider_info()
    assert info["provider_name"] == "helenaimoveis"
    assert "search_rentals" in info["supported_operations"]


def test_mcp_adapter_search_rentals():
    """Test MCP search tool execution."""
    adapter = HelenaMcpAdapter(service=DummyService())
    res = adapter.search_rentals(city="Timóteo", bedrooms=2, max_price=1500.0)
    assert isinstance(res, dict)
    assert res["provider"] == "helenaimoveis"
    assert len(res["listings"]) == 1


def test_mcp_adapter_property_detail():
    """Test MCP property detail tool execution."""
    adapter = HelenaMcpAdapter(service=DummyService())
    detail = adapter.get_property_detail("999")
    assert isinstance(detail, dict)
    assert detail["title"] == "Apto Centro Timóteo"
