"""Domain exception hierarchy for Helena Imóveis rental research."""


class HelenaResearchError(Exception):
    """Base exception for all domain and infrastructure errors."""


class PortalConnectionError(HelenaResearchError):
    """Raised when portal network communication fails."""


class PropertyNotFoundError(HelenaResearchError):
    """Raised when a requested property cannot be found or redirects home."""


class ParsingError(HelenaResearchError):
    """Raised when HTML or JSON response structure cannot be parsed."""


class InvalidCriteriaError(HelenaResearchError):
    """Raised when search parameters violate domain validation rules."""
