import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

HYBRID_FILE = PROJECT_ROOT / "product" / "68_integrated_hybrid_search.py"


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hybrid_module = load_module(
    "integrated_hybrid_search",
    HYBRID_FILE
)


class ProductRecommendationEngine:

    def __init__(self, top_k=5):
        self.searcher = hybrid_module.IntegratedHybridSearch(
            top_k=20
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

    def recommend(self, customer_query):

        search_result = self.searcher.search(customer_query)

        ranked_products = self.rank_products(
            search_result["results"]
        )

        return {
            "query": customer_query,
            "filters": search_result["filters"],
            "keywords": search_result["keywords"],
            "results": ranked_products[:self.top_k]
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT RECOMMENDATION ENGINE")
    print("=" * 60)

    engine = ProductRecommendationEngine(top_k=5)

    queries = [
        "I want oxidized earrings under 300 that are available",
        "Show me earrings under 200",
        "I want oxidized jewellery"
    ]

    for query in queries:

        print()
        print("-" * 60)
        print(f"Customer Query: {query}")
        print("-" * 60)

        result = engine.recommend(query)

        print()
        print(f"Keywords: {result['keywords']}")
        print(f"Matching Products: {len(result['results'])}")

        for rank, product in enumerate(
            result["results"],
            start=1
        ):

            stock = (
                "In Stock"
                if product["in_stock"]
                else "Out of Stock"
            )

            print()
            print(f"Rank: {rank}")
            print(f"Name: {product['name']}")
            print(f"Price: ₹{product['price']}")
            print(f"Stock: {stock}")
            print(f"Semantic Score: {product['score']:.4f}")
            print(f"URL: {product['url']}")

    print()
    print("=" * 60)
    print("PRODUCT RECOMMENDATION COMPLETED")
    print("=" * 60)