import json
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCT_FILE = (
    PROJECT_ROOT
    / "data"
    / "products"
    / "products_stock_normalized.json"
)

CARD_FILE = (
    PROJECT_ROOT
    / "product"
    / "69_product_recommendation.py"
)


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class APIProductResponse:

    def __init__(self):

        self.products = self.load_products()

        recommendation_module = load_module(
            "product_recommendation",
            CARD_FILE
        )

        self.recommender = (
            recommendation_module.ProductRecommendationEngine(
                top_k=5
            )
        )

    def load_products(self):

        with open(
            PRODUCT_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def create_response(self, customer_query):

        recommendation = (
            self.recommender.recommend(
                customer_query
            )
        )

        product_map = {
            product.get("url"): product
            for product in self.products
        }

        products = []

        for result in recommendation["results"]:

            product = product_map.get(
                result.get("url")
            )

            if not product:
                continue

            products.append({
                "name": product.get("name"),
                "price": product.get("price"),
                "in_stock": product.get("in_stock"),
                "stock_label": product.get(
                    "stock_label",
                    "Stock Unknown"
                ),
                "categories": product.get(
                    "categories",
                    []
                ),
                "tags": product.get(
                    "tags",
                    []
                ),
                "description": product.get(
                    "description",
                    ""
                ),
                "image": product.get(
                    "image"
                ),
                "url": product.get(
                    "url"
                )
            })

        return {
            "success": True,
            "query": customer_query,
            "filters": recommendation["filters"],
            "keywords": recommendation["keywords"],
            "product_count": len(products),
            "products": products
        }


if __name__ == "__main__":

    service = APIProductResponse()

    query = "I want oxidized jewellery"

    response = service.create_response(query)

    print("=" * 60)
    print("ZYRA LUXE - API PRODUCT RESPONSE")
    print("=" * 60)

    print()

    print(
        json.dumps(
            response,
            indent=2,
            ensure_ascii=False
        )
    )