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

ROUTER_FILE = (
    PROJECT_ROOT
    / "product"
    / "80_zyra_query_router.py"
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

        router_module = load_module(
            "zyra_query_router_product_response",
            ROUTER_FILE
        )

        self.recommender = (
            recommendation_module.ProductRecommendationEngine(
                top_k=5
            )
        )

        self.router = router_module.ZyraQueryRouter()

    def load_products(self):

        with open(
            PRODUCT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def get_previous_product_query(
        self,
        history
    ):

        for message in reversed(history):

            if message.get("role") != "user":
                continue

            previous_query = message.get(
                "content",
                ""
            ).strip()

            if not previous_query:
                continue

            if self.router.route(
                previous_query
            ) == "PRODUCT":

                return previous_query

        return None

    def get_shown_product_urls(
        self,
        history
    ):

        shown_urls = []

        for message in history:

            if message.get("role") != "assistant":
                continue

            products = message.get(
                "products",
                []
            )

            for product in products:

                url = product.get("url")

                if url and url not in shown_urls:

                    shown_urls.append(url)

        return shown_urls

    def resolve_query(
        self,
        customer_query,
        history=None
    ):

        if history is None:
            history = []

        if not self.router.is_follow_up(
            customer_query
        ):

            return customer_query

        previous_product_query = (
            self.get_previous_product_query(
                history
            )
        )

        if previous_product_query:

            return previous_product_query

        return customer_query

    def create_response(
        self,
        customer_query,
        history=None
    ):

        if history is None:
            history = []

        is_follow_up = self.router.is_follow_up(
            customer_query
        )

        search_query = self.resolve_query(
            customer_query,
            history
        )

        exclude_urls = []

        if is_follow_up:

            exclude_urls = (
                self.get_shown_product_urls(
                    history
                )
            )

        print(
            f"Product search query: {search_query}"
        )

        print(
            f"Excluded product URLs: "
            f"{len(exclude_urls)}"
        )

        recommendation = (
            self.recommender.recommend(
                search_query,
                exclude_urls=exclude_urls
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
            "query": search_query,
            "original_query": customer_query,
            "filters": recommendation["filters"],
            "keywords": recommendation["keywords"],
            "product_count": len(products),
            "products": products
        }


if __name__ == "__main__":

    service = APIProductResponse()

    print("=" * 60)
    print("ZYRA LUXE - API PRODUCT RESPONSE")
    print("=" * 60)

    print()
    print("1. Direct product query")

    response = service.create_response(
        "Show me oxidized jewellery"
    )

    print()
    print(
        json.dumps(
            response,
            indent=2,
            ensure_ascii=False
        )
    )

    print()
    print("-" * 60)
    print("2. Product follow-up")
    print("-" * 60)

    first_response = service.create_response(
        "Show me oxidized jewellery"
    )

    history = [
        {
            "role": "user",
            "content": "Show me oxidized jewellery"
        },
        {
            "role": "assistant",
            "content": "I found 5 products.",
            "products": first_response["products"]
        }
    ]

    response = service.create_response(
        "Show me more",
        history
    )

    print()
    print(
        json.dumps(
            response,
            indent=2,
            ensure_ascii=False
        )
    )