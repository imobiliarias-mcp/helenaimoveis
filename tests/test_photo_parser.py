"""Unit tests for AJAX photo endpoint parser."""

from helena_research.parsers.photo_parser import PhotoParser


def test_parse_valid_photo_json() -> None:
    """Test parsing typical ImobiBrasil AJAX photo response."""
    raw = (
        '{"0":{"codigo_imo":"4356012","arquivo_imm":"img1.jpeg"},'
        '"1":{"codigo_imo":"4356012","arquivo_imm":"img2.jpeg"}}'
    )
    parser = PhotoParser()
    gallery = parser.parse(raw)
    assert len(gallery) == 2
    assert gallery[0] == "https://www.helenaimoveis.com.br/imagens/imoveis/img1.jpeg"
    assert gallery[1] == "https://www.helenaimoveis.com.br/imagens/imoveis/img2.jpeg"
    assert gallery.first_photo() == "https://www.helenaimoveis.com.br/imagens/imoveis/img1.jpeg"


def test_parse_empty_or_invalid_json() -> None:
    """Test resilience against empty or malformed inputs."""
    parser = PhotoParser()
    assert len(parser.parse("")) == 0
    assert len(parser.parse("{}")) == 0
    assert len(parser.parse("not json")) == 0
    assert len(parser.parse("[]")) == 0
