# Helena Imóveis — Central Rental Research MCP Adapter

Reverse-engineered rental search engine and client library for **Helena Imóveis** (`https://www.helenaimoveis.com.br/`).

Engineered as a pluggable adapter for the **Central Rental Research MCP (Model Context Protocol)** server boundary following **SOLID**, **Clean Code**, **Object Calisthenics**, and **Design Patterns** in Python.

---

## 📚 Documentation

- **[Documentation Index](file:///home/samuelcaldas/repos/imobiliarias/helenaimoveis/docs/README.md)** (`docs/README.md`): Overview of all project documentation.
- **[Reverse-Engineered Rental Search API Documentation](file:///home/samuelcaldas/repos/imobiliarias/helenaimoveis/docs/api-research.md)** (`docs/api-research.md`): In-depth research notes on ImobiBrasil routing, DOM structure, Schema.org JSON-LD microdata, parameter mappings, and AJAX media endpoints.
- **[Research Plan & Verification Log](file:///home/samuelcaldas/repos/imobiliarias/helenaimoveis/scripts/research-plan.md)** (`scripts/research-plan.md`): Step-by-step methodology, boundary sensitivity analysis, and empirical verification test matrix.

---

## ⚡ Quickstart

### Environment Setup
```bash
# Create virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Run Automated Tests
```bash
.venv/bin/pytest -v
```

### Run Empirical Verification Script
```bash
.venv/bin/python3 scripts/run_research.py
```

### Python SDK Usage
```python
from helena_research import HelenaResearchService, SearchCriteria, PropertyType

service = HelenaResearchService()

# 1. Search rentals with 2 bedrooms in Timóteo
criteria = SearchCriteria.create_rental(city="timoteo", bedrooms=2)
results = service.search_rentals(criteria)

for item in results:
    print(item.identity.property_id, item.title, item.price_text)

# 2. Retrieve property detail
detail = service.get_property_detail("4356012")
print(detail.overview.title, detail.pricing.amount, detail.location.address)

# 3. Retrieve property photos via AJAX endpoint
photos = service.get_property_photos("4356012")
print("Total photos:", len(photos))
```

---

## 🏛️ Code Architecture & Standards Compliance

- **Correctness First**: All 31 unit and live integration tests passing.
- **Modularity Second**: Hexagonal separation into `domain`, `infrastructure`, `parsers`, and `application` layers.
- **Object Calisthenics**:
  - **No `else` Keyword**: 100% eliminated using guard clauses and early returns.
  - **Single Level of Indentation**: All methods adhere to at most 1 indent level.
  - **Wrapped Primitives**: Domain concepts (`PriceRange`, `AreaRange`, `RoomCount`, `PageNumber`) are validated Value Objects.
  - **First-Class Collections**: `ListingCollection` and `PhotoGallery` encapsulate collection behaviors.
  - **Size Limits**: Functions ≤ 15 lines, Classes ≤ 100 lines, Modules < 200 lines.
  - **Instance Variables**: Classes hold at most 2 instance variables (using coordinators).
  - **One Dot per Line**: Method chaining is eliminated in favor of explicit intermediate assignments.
  - **Descriptive Naming**: Full, descriptive domain identifiers without abbreviations.
