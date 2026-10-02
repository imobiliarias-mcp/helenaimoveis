# Helena Imóveis — Documentation Index

Welcome to the documentation for the **Helena Imóveis** (`helenaimoveis.com.br`) rental search research and adapter library.

---

## 📑 Core Documentation

- **[Reverse-Engineered Rental Search API Documentation](file:///home/samuelcaldas/repos/imobiliarias/helenaimoveis/docs/api-research.md)** (`docs/api-research.md`):  
  Comprehensive reverse-engineering report documenting the ImobiBrasil web platform, canonical SEO paths, query parameter formats, pagination behavior, property detail extraction (JSON-LD + HTML), and AJAX photo gallery endpoints.

- **[Research Plan & Execution Log](file:///home/samuelcaldas/repos/imobiliarias/helenaimoveis/scripts/research-plan.md)** (`scripts/research-plan.md`):  
  Detailed methodology, empirical test matrix (13 test cases verified against live portal), parameter boundary checks, and central MCP boundary specifications.
- Search results expose an absolute public-property `url` while retaining native `url_path` and collection pagination metadata; see the API research document's search-card section.

---

## 🛠️ Architecture & Clean Code Compliance

The Python implementation in `src/helena_research/` strictly adheres to:
1. **SOLID Principles**:
   - Single Responsibility: Parsers, builders, and transport have dedicated roles.
   - Open/Closed: Domain entities extend through composition and protocols.
   - Interface Segregation: Focused protocols (`RentalSearchPort`, `PropertyDetailPort`, `PropertyMediaPort`).
   - Dependency Inversion: Service depends on abstractions (`HttpClientProtocol`, `RentalSearchPort`).
2. **Object Calisthenics**:
   - One indentation level per method.
   - No `else` statements (early returns and guard clauses).
   - Domain primitives wrapped in Value Objects (`PriceRange`, `RoomCount`, `PageNumber`).
   - First-class collections (`ListingCollection`, `PhotoGallery`).
   - One dot per line.
   - Small entities (functions ≤ 15 lines, classes ≤ 100 lines, modules < 200 lines).
   - At most 2 instance variables per class.
