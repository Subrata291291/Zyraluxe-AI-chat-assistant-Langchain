import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

HYBRID_FILE = (
    PROJECT_ROOT
    / "product"
    / "68_integrated_hybrid_search.py"
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


hybrid_module = load_module(
    "integrated_hybrid_search",
    HYBRID_FILE
)


class ProductRecommendationEngine:

    def __init__(self, top_k=5):

        self.searcher = (
            hybrid_module.IntegratedHybridSearch(
                top_k=50
            )
        )

        self.top_k = top_k

    def rank_products(self, products):

        def recommendation_score(product):

            score = product["score"]

            if product["in_stock"] is True:
                score += 0.10

            if product["price"] is not None:

                if product["price"] <= 300:
                    score += 0.02

            return score

        return sorted(
            products,
            key=recommendation_score,
            reverse=True
        )

    def recommend(
        self,
        customer_query,
        exclude_urls=None
    ):

        if exclude_urls is None:
            exclude_urls = []

        exclude_urls = set(
            exclude_urls
        )

        search_result = self.searcher.search(
            customer_query
        )

        ranked_products = self.rank_products(
            search_result["results"]
        )

        filtered_products = [
            product
            for product in ranked_products
            if product.get("url")
            not in exclude_urls
        ]

        return {
            "query": customer_query,
            "filters": search_result["filters"],
            "keywords": search_result["keywords"],
            "results": filtered_products[:self.top_k]
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT RECOMMENDATION ENGINE")
    print("=" * 60)

    engine = ProductRecommendationEngine(
        top_k=5
    )

    query = "I want oxidized jewellery"

    print()
    print("-" * 60)
    print("1. Normal Recommendation")
    print("-" * 60)

    result = engine.recommend(
        query
    )

    print()
    print(
        f"Keywords: "
        f"{result['keywords']}"
    )

    print(
        f"Matching Products: "
        f"{len(result['results'])}"
    )

    for rank, product in enumerate(
        result["results"],
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
    print("-" * 60)
    print("2. Exclusion Test")
    print("-" * 60)

    excluded_urls = [
        product["url"]
        for product in result["results"]
    ]

    print()
    print(
        f"Excluded Products: "
        f"{len(excluded_urls)}"
    )

    next_result = engine.recommend(
        query,
        exclude_urls=excluded_urls
    )

    print()
    print(
        f"New Products: "
        f"{len(next_result['results'])}"
    )

    for rank, product in enumerate(
        next_result["results"],
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
    print("PRODUCT RECOMMENDATION COMPLETED")
    print("=" * 60)