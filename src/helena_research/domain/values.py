"""Domain value objects representing search parameters and constraints."""

from dataclasses import dataclass
from helena_research.domain.exceptions import InvalidCriteriaError


@dataclass(frozen=True)
class PriceRange:
    """Encapsulates minimum and maximum price constraints in Brazilian Reais."""

    minimum: int | None = None
    maximum: int | None = None

    def __post_init__(self) -> None:
        """Validate price constraints."""
        if self.minimum is not None and self.minimum < 0:
            raise InvalidCriteriaError("Minimum price must be non-negative")
        if self.maximum is not None and self.maximum < 0:
            raise InvalidCriteriaError("Maximum price must be non-negative")
        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            raise InvalidCriteriaError("Minimum price cannot exceed maximum price")

    def query_parameters(self) -> dict[str, str]:
        """Convert price range to URL query parameters."""
        params: dict[str, str] = {}
        if self.minimum is not None:
            params["vmi"] = str(self.minimum)
        if self.maximum is not None:
            params["vma"] = str(self.maximum)
        return params


@dataclass(frozen=True)
class AreaRange:
    """Encapsulates minimum and maximum square meters constraints."""

    minimum: int | None = None
    maximum: int | None = None

    def __post_init__(self) -> None:
        """Validate area constraints."""
        if self.minimum is not None and self.minimum < 0:
            raise InvalidCriteriaError("Minimum area must be non-negative")
        if self.maximum is not None and self.maximum < 0:
            raise InvalidCriteriaError("Maximum area must be non-negative")
        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            raise InvalidCriteriaError("Minimum area cannot exceed maximum area")

    def query_parameters(self) -> dict[str, str]:
        """Convert area range to URL query parameters."""
        params: dict[str, str] = {}
        if self.minimum is not None:
            params["areaMinima"] = str(self.minimum)
        if self.maximum is not None:
            params["areaMaxima"] = str(self.maximum)
        return params


@dataclass(frozen=True)
class RoomCount:
    """Represents a room quantity constraint (exact count or 'N or more')."""

    count: int
    is_minimum: bool = False

    def __post_init__(self) -> None:
        """Enforce valid range 1 to 5 for platform selectors."""
        if self.count < 1 or self.count > 5:
            raise InvalidCriteriaError("Room count must be between 1 and 5")

    def to_param_code(self) -> str:
        """Convert room count to ImobiBrasil parameter code."""
        if not self.is_minimum:
            return str(self.count)
        return str(20 + self.count)


@dataclass(frozen=True)
class PageNumber:
    """Represents a 1-indexed pagination number."""

    value: int = 1

    def __post_init__(self) -> None:
        """Enforce positive page index."""
        if self.value < 1:
            raise InvalidCriteriaError("Page index must be greater than or equal to 1")

    def to_param_code(self) -> str:
        """Return the string representation for query string."""
        return str(self.value)
