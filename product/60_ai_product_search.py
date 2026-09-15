import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PARSER_FILE = (
    PROJECT_ROOT
    / "product"
    / "59_llm_product_query_parser.py"
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

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load {file_path}"
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return getattr(module, class_name)


LLMProductQueryParser = load_class(
    PARSER_FILE,
    "LLMProductQueryParser"
)

SearchRank = load_class(
    SEARCH_RANK_FILE,
    "SearchRank"
)


class AIProductSearch:

    def __init__(self):

        self.parser = LLMProductQueryParser()
        self.search_rank = SearchRank()

    def search(self, customer_query):

        filters = self.parser.parse(
            customer_query
        )

        results = self.search_rank.search_and_rank(
            query=filters.get("query"),
            max_price=filters.get("max_price"),
            category=filters.get("category"),
            in_stock=filters.get("in_stock")
        )

        return filters, results


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - AI PRODUCT SEARCH")
    print("=" * 60)

    engine = AIProductSearch()

    query = (
        "I need oxidized earrings "
        "under 300 that are available"
    )

    print()
    print(f"Customer Query: {query}")

    try:

        filters, results = engine.search(query)

        print()
        print(f"LLM Filters: {filters}")

        print()
        print(
            f"Matching Products: "
            f"{len(results)}"
        )

        for index, product in enumerate(
            results[:5],
            start=1
        ):

            print("-" * 60)

            print(f"Rank: {index}")
            print(f"Name: {product['name']}")
            print(f"Price: ₹{product['price']}")
            print(
                f"Stock: "
                f"{product['in_stock']}"
            )
            print(f"URL: {product['url']}")

    except Exception as error:

        print()
        print(f"Error: {error}")

    print()
    print("=" * 60)
    print("AI PRODUCT SEARCH CHECK COMPLETED")
    print("=" * 60)