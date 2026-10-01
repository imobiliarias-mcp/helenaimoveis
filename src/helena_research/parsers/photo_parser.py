"""Parser for property photo gallery endpoint responses."""

import json
from helena_research.domain.property import PhotoGallery


class PhotoParser:
    """Parses JSON photo gallery responses from ImobiBrasil backend."""

    def __init__(self, base_media_url: str = "https://www.helenaimoveis.com.br/imagens/imoveis") -> None:
        """Initialize with base media image directory."""
        self.base_media_url = base_media_url.rstrip("/")

    def parse(self, json_content: str) -> PhotoGallery:
        """Parse JSON response into PhotoGallery domain collection."""
        if not json_content or not json_content.strip():
            return PhotoGallery()
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError:
            return PhotoGallery()
        if not isinstance(data, dict):
            return PhotoGallery()
        urls = self._extract_urls(data)
        return PhotoGallery(photo_urls=tuple(urls))

    def _extract_urls(self, data: dict[str, object]) -> list[str]:
        """Extract and format full image URLs from JSON dictionary."""
        urls: list[str] = []
        for key in sorted(data.keys(), key=self._sort_key):
            item = data[key]
            if isinstance(item, dict) and "arquivo_imm" in item:
                filename = str(item["arquivo_imm"])
                urls.append(f"{self.base_media_url}/{filename}")
        return urls

    def _sort_key(self, key: str) -> int:
        """Helper to sort dictionary keys numerically."""
        try:
            return int(key)
        except ValueError:
            return 9999
