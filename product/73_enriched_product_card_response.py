import json
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCT_FILE = PROJECT_ROOT / "data" / "products" / "products_enriched.json"
RECOMMENDATION_FILE = PROJECT_ROOT / "product" / "69_product_recommendation.py"


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EnrichedProductCardResponse:

    def __init__(self):
        self.products = self.load_products()

        recommendation_module = load_module(
            "product_recommendation",
            RECOMMENDATION_FILE
        )

        self.recommender = (
            recommendation_module.ProductRecommendationEngine()
        )

    def load_products(self):
        with open(PRODUCT_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def create_cards(self, customer_query):

        recommendation = self.recommender.recommend(
            customer_query
        )

        product_map = {
            product.get("url"): product
            for product in self.products
        }

        cards = []

        for product in recommendation["results"]:

            full_product = product_map.get(
                product.get("url"),
                {}
            )

            card = {
                "name": full_product.get("name"),
                "price": full_product.get("price"),
                "in_stock": full_product.get("in_stock"),
                "stock_label": (
                    "In Stock"
                    if full_product.get("in_stock") is True
                    else "Out of Stock"
                ),
                "categories": full_product.get(
                    "categories",
                    []
                ),
                "tags": full_product.get(
                    "tags",
                    []
                ),
                "description": full_product.get(
                    "description"
                ),
                "image": full_product.get(
                    "image"
                ),
                "url": full_product.get(
                    "url"
                ),
                "score": product.get(
                    "score"
                )
            }

            cards.append(card)

        return {
            "query": recommendation["query"],
            "filters": recommendation["filters"],
            "keywords": recommendation["keywords"],
            "results": cards
        }


if __name__ == "__main__":

    service = EnrichedProductCardResponse()

    query = "I want oxidized jewellery"

    response = service.create_cards(query)

    print("=" * 60)
    print("ZYRA LUXE - ENRICHED PRODUCT CARD RESPONSE")
    print("=" * 60)

    print()
    print(f"Query: {response['query']}")
    print(f"Keywords: {response['keywords']}")
    print(f"Products Found: {len(response['results'])}")

    for index, card in enumerate(
        response["results"],
        start=1
    ):

        print()
        print(f"--- Product {index} ---")
        print(f"Name: {card['name']}")
        print(f"Price: ₹{card['price']}")
        print(f"Stock: {card['stock_label']}")
        print(f"Categories: {card['categories']}")
        print(f"Tags: {card['tags']}")
        print(f"Image: {card['image']}")
        print(f"URL: {card['url']}")
        print(f"Score: {card['score']}")