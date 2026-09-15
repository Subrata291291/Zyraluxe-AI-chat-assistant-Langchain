import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SEARCH_FILE = PROJECT_ROOT / "product" / "54_product_search.py"
RANKING_FILE = PROJECT_ROOT / "product" / "55_product_ranking.py"


def load_class(file_path, class_name):

    spec = importlib.util.spec_from_file_location(
        class_name,
        file_path
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, class_name)


ProductSearch = load_class(
    SEARCH_FILE,
    "ProductSearch"
)

ProductRanking = load_class(
    RANKING_FILE,
    "ProductRanking"
)


class SearchRank:

    def __init__(self):

        self.search = ProductSearch()
        self.ranking = ProductRanking()

    def search_and_rank(
        self,
        query=None,
        max_price=None,
        category=None,
        in_stock=None
    ):

        products = self.search.search(
            query=query,
            max_price=max_price,
            category=category,
            in_stock=in_stock
        )

        return self.ranking.rank(products)


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - SEARCH + RANKING")
    print("=" * 60)

    engine = SearchRank()

    results = engine.search_and_rank(
        category="earrings",
        max_price=300,
        in_stock=True
    )

    print()
    print(f"Matching Products: {len(results)}")

    for index, product in enumerate(results, start=1):

        print("-" * 60)

        print(f"Rank: {index}")
        print(f"Name: {product['name']}")
        print(f"Price: ₹{product['price']}")
        print(f"Stock: {product['in_stock']}")

    print()
    print("=" * 60)
    print("SEARCH + RANKING CHECK COMPLETED")
    print("=" * 60)