import importlib.util
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RECOMMENDATION_FILE = (
    PROJECT_ROOT / "product" / "69_product_recommendation.py"
)

PRODUCT_FILE = (
    PROJECT_ROOT / "data" / "products" / "products.json"
)


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


recommendation_module = load_module(
    "product_recommendation",
    RECOMMENDATION_FILE
)


class ProductCardResponse:

    def __init__(self, top_k=5):
        self.engine = (
            recommendation_module.ProductRecommendationEngine(
                top_k=top_k
            )
        )

        self.products = self.load_products()

    def load_products(self):

        with open(
            PRODUCT_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def create_product_map(self):

        return {
            product["url"]: product
            for product in self.products
        }

    def create_card(self, product, product_map):

        full_product = product_map.get(
            product.get("url"),
            {}
        )

        return {
            "name": full_product.get(
                "name",
                product.get("name")
            ),
            "price": full_product.get(
                "price",
                product.get("price")
            ),
            "in_stock": full_product.get(
                "in_stock",
                product.get("in_stock")
            ),
            "stock_label": (
                "In Stock"
                if full_product.get(
                    "in_stock",
                    product.get("in_stock")
                )
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
                "description",
                ""
            ),
            "url": full_product.get(
                "url",
                product.get("url")
            )
        }

    def search(self, customer_query):

        recommendation = self.engine.recommend(
            customer_query
        )

        product_map = self.create_product_map()

        cards = [
            self.create_card(
                product,
                product_map
            )
            for product in recommendation["results"]
        ]

        return {
            "query": customer_query,
            "products": cards
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT CARD RESPONSE")
    print("=" * 60)

    response_builder = ProductCardResponse(
        top_k=5
    )

    query = "I want oxidized jewellery"

    result = response_builder.search(query)

    print()
    print(f"Customer Query: {result['query']}")
    print()
    print(f"Product Cards: {len(result['products'])}")

    for index, card in enumerate(
        result["products"],
        start=1
    ):

        print()
        print(f"Card {index}")
        print(f"Name: {card['name']}")
        print(f"Price: ₹{card['price']}")
        print(f"Stock: {card['stock_label']}")
        print(f"Categories: {card['categories']}")
        print(f"Tags: {card['tags']}")
        print(f"Description: {card['description']}")
        print(f"URL: {card['url']}")

    print()
    print("=" * 60)
    print("PRODUCT CARD RESPONSE COMPLETED")
    print("=" * 60)