import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from helena_research.application.service import HelenaResearchService
from helena_research.domain.criteria import SearchCriteria


def main() -> None:
    """Run empirical verification suite against live portal."""
    service = HelenaResearchService()
    print("=" * 70)
    print("HELENA IMÓVEIS RENTAL RESEARCH - EMPIRICAL VERIFICATION")
    print("=" * 70)

    # 1. Target URL verification from prompt
    target_url = "https://www.helenaimoveis.com.br/imovel/locacao/todos/timoteo/?&dormitorios=2"
    print(f"\n1. Target URL Search: {target_url}")
    target_results = service.search_by_url(target_url)
    print(f"   Returned: {len(target_results)} property card(s)")
    for item in target_results:
        print(f"   - ID: {item.identity.property_id} | Ref: {item.reference_code} | Price: {item.price_text}")
        print(f"     Title: {item.title}")
        print(f"     Location: {item.location.neighborhood}, {item.location.city} / {item.location.state}")
        print(f"     Specs: {item.specs.bedrooms} dorm(s), {item.specs.bathrooms} bath(s), {item.specs.parking_spaces} parking")
        print(f"     Link: {item.url}")

    # 2. Domain criteria query
    print("\n2. Domain Criteria Search (Timóteo, Rental, Max R$ 1.500):")
    criteria = SearchCriteria.create_rental(city="timoteo", max_price=1500)
    filtered_results = service.search_rentals(criteria)
    print(f"   Returned: {len(filtered_results)} property card(s)")
    for item in filtered_results[:3]:
        print(f"   - ID: {item.identity.property_id} | Price: {item.price_text} | Bairro: {item.location.neighborhood}")
        print(f"     Link: {item.url}")

    # 3. Property Detail Retrieval
    if not target_results.is_empty():
        prop_id = target_results[0].identity.property_id
        print(f"\n3. Property Detail Retrieval (ID: {prop_id}):")
        detail = service.get_property_detail(prop_id)
        print(f"   Title: {detail.overview.title}")
        print(f"   Ref: {detail.overview.reference_code}")
        print(f"   Address: {detail.location.address}, {detail.location.neighborhood}")
        print(f"   Rent Amount: {detail.pricing.formatted_text} (Numeric: {detail.pricing.amount})")
        print(f"   IPTU: {detail.pricing.iptu}")
        print(f"   Condo Fee: {detail.pricing.condo_fee}")
        print(f"   Specs: {detail.specs.bedrooms} dorm(s), {detail.specs.bathrooms} bath(s), {detail.specs.parking_spaces} garage(s)")
        print(f"   Characteristics ({len(detail.characteristics)}): {', '.join(detail.characteristics[:5])}...")
        print(f"   Photos ({len(detail.photos)}): First -> {detail.photos.first_photo()}")

        # 4. Property Photos AJAX
        print(f"\n4. AJAX Photo Gallery Retrieval (ID: {prop_id}):")
        ajax_photos = service.get_property_photos(prop_id)
        print(f"   Returned: {len(ajax_photos)} photo(s)")
        for idx, photo_url in enumerate(ajax_photos[:3]):
            print(f"   [{idx + 1}] {photo_url}")

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
