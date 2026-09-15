import json
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CARD_FILE = PROJECT_ROOT / "product" / "73_enriched_product_card_response.py"


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProductResponseJSON:

    def __init__(self):
        card_module = load_module(
            "enriched_product_card_response",
            CARD_FILE
        )

        self.card_service = (
            card_module.EnrichedProductCardResponse()
        )

    def create_response(self, customer_query):

        card_response = self.card_service.create_cards(
            customer_query
        )

        products = []

        for card in card_response["results"]:

            product = {
                "name": card["name"],
                "price": card["price"],
                "in_stock": card["in_stock"],
                "stock_label": card["stock_label"],
                "categories": card["categories"],
                "tags": card["tags"],
                "description": card["description"],
                "image": card["image"],
                "url": card["url"]
            }

            products.append(product)

        return {
            "query": card_response["query"],
            "filters": card_response["filters"],
            "keywords": card_response["keywords"],
            "product_count": len(products),
            "products": products
        }


if __name__ == "__main__":

    service = ProductResponseJSON()

    query = "I want oxidized jewellery"

    response = service.create_response(query)

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT RESPONSE JSON")
    print("=" * 60)

    print()

    print(
        json.dumps(
            response,
            indent=2,
            ensure_ascii=False
        )
    )