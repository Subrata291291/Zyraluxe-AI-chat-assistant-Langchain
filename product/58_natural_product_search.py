import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PARSER_FILE = (
    PROJECT_ROOT
    / "product"
    / "57_product_query_parser.py"
)

SEARCH_RANK_FILE = (
    PROJECT_ROOT
    / "product"
    / "56_search_rank.py"
)


def load_class(file_path, class_name):

    spec = importlib.util.spec_from_file_location(
        class_name,
        file_path
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, class_name)


ProductQueryParser = load_class(
    PARSER_FILE,
    "ProductQueryParser"
)

SearchRank = load_class(
    SEARCH_RANK_FILE,
    "SearchRank"
)


class NaturalProductSearch:

    def __init__(self):

        self.parser = ProductQueryParser()
        self.search_rank = SearchRank()

    def search(self, customer_query):

        filters = self.parser.parse(customer_query)

        results = self.search_rank.search_and_rank(
            query=filters["query"],
            max_price=filters["max_price"],
            category=filters["category"],
            in_stock=filters["in_stock"]
        )

        return filters, results


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - NATURAL PRODUCT SEARCH")
    print("=" * 60)

    engine = NaturalProductSearch()

    queries = [
        "Show me earrings under ₹300 that are available",
        "I want necklace below 500",
        "Show me bangles upto ₹200"
    ]

    for query in queries:

        filters, results = engine.search(query)

        print()
        print("-" * 60)
        print(f"Customer Query: {query}")
        print(f"Filters: {filters}")
        print(f"Products Found: {len(results)}")

        for index, product in enumerate(results[:5], start=1):

            print(
                f"{index}. "
                f"{product['name']} | "
                f"₹{product['price']} | "
                f"Stock: {product['in_stock']}"
            )

    print()
    print("=" * 60)
    print("NATURAL PRODUCT SEARCH CHECK COMPLETED")
    print("=" * 60)