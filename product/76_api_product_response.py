import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCT_API_FILE = (
    PROJECT_ROOT
    / "product"
    / "92_woocommerce_product_api.py"
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

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load module: {file_path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(module)

    return module


class APIProductResponse:

    def __init__(self):

        recommendation_module = load_module(
            "product_recommendation",
            CARD_FILE
        )

        router_module = load_module(
            "zyra_query_router_product_response",
            ROUTER_FILE
        )

        product_api_module = load_module(
            "woocommerce_product_api_response",
            PRODUCT_API_FILE
        )

        self.recommender = (
            recommendation_module.ProductRecommendationEngine(
                top_k=5
            )
        )

        self.router = (
            router_module.ZyraQueryRouter()
        )

        self.product_api = (
            product_api_module.WooCommerceProductAPI()
        )

    def get_live_products(self):

        all_products = []

        page = 1

        while True:

            response = self.product_api.get_products(
                page=page,
                per_page=100
            )

            products = response.get(
                "products",
                []
            )

            all_products.extend(
                products
            )

            total_products = response.get(
                "total_products",
                0
            )

            if not products:
                break

            if len(all_products) >= total_products:
                break

            page += 1

        return all_products

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

    def normalize_product(
        self,
        product
    ):

        categories = [
            category.get("name", "")
            for category in product.get(
                "categories",
                []
            )
        ]

        tags = [
            tag.get("name", "")
            for tag in product.get(
                "tags",
                []
            )
        ]

        images = product.get(
            "images",
            []
        )

        image = None

        if images:

            image = images[0].get(
                "src"
            )

        stock_status = product.get(
            "stock_status"
        )

        in_stock = (
            stock_status == "instock"
        )

        stock_label = (
            "In Stock"
            if in_stock
            else "Out of Stock"
        )

        price = product.get(
            "price"
        )

        if price not in (
            None,
            ""
        ):

            try:
                price = float(price)
            except (
                TypeError,
                ValueError
            ):
                price = None

        return {
            "name": product.get(
                "name"
            ),
            "price": price,
            "in_stock": in_stock,
            "stock_label": stock_label,
            "categories": categories,
            "tags": tags,
            "description": (
                product.get(
                    "short_description"
                )
                or product.get(
                    "description"
                )
                or ""
            ),
            "image": image,
            "url": product.get(
                "permalink"
            )
        }

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
            f"Product search query: "
            f"{search_query}"
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

        live_products = (
            self.get_live_products()
        )

        product_map = {
            product.get("permalink"): product
            for product in live_products
            if product.get("permalink")
        }

        products = []

        for result in recommendation["results"]:

            url = result.get(
                "url"
            )

            product = product_map.get(
                url
            )

            if not product:
                continue

            products.append(
                self.normalize_product(
                    product
                )
            )

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
    print("ZYRA LUXE - LIVE API PRODUCT RESPONSE")
    print("=" * 60)

    print()
    print("1. Direct product query")

    response = service.create_response(
        "Show me oxidized jewellery"
    )

    print()
    print(
        f"Products Returned: "
        f"{response['product_count']}"
    )

    for rank, product in enumerate(
        response["products"],
        start=1
    ):

        print()
        print(
            f"Rank: {rank}"
        )

        print(
            f"Name: "
            f"{product['name']}"
        )

        print(
            f"Price: "
            f"₹{product['price']}"
        )

        print(
            f"Stock: "
            f"{product['stock_label']}"
        )

        print(
            f"Image: "
            f"{product['image']}"
        )

        print(
            f"URL: "
            f"{product['url']}"
        )

    print()
    print("-" * 60)
    print("2. Product follow-up")
    print("-" * 60)

    history = [
        {
            "role": "user",
            "content": "Show me oxidized jewellery"
        },
        {
            "role": "assistant",
            "content": "I found products.",
            "products": response["products"]
        }
    ]

    next_response = service.create_response(
        "Show me more",
        history
    )

    print()
    print(
        f"New Products Returned: "
        f"{next_response['product_count']}"
    )

    for rank, product in enumerate(
        next_response["products"],
        start=1
    ):

        print()
        print(
            f"Rank: {rank}"
        )

        print(
            f"Name: "
            f"{product['name']}"
        )

        print(
            f"Price: "
            f"₹{product['price']}"
        )

        print(
            f"URL: "
            f"{product['url']}"
        )

    print()
    print("=" * 60)
    print(
        "LIVE API PRODUCT RESPONSE COMPLETED"
    )
    print("=" * 60)