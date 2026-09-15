import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARSER_FILE = PROJECT_ROOT / "product" / "59_llm_product_query_parser.py"
NORMALIZER_FILE = PROJECT_ROOT / "product" / "67_product_keyword_normalizer.py"
SEMANTIC_FILE = PROJECT_ROOT / "product" / "64_semantic_product_search.py"
PRODUCT_SEARCH_FILE = PROJECT_ROOT / "product" / "54_product_search.py"


parser_module = load_module("llm_parser", PARSER_FILE)
normalizer_module = load_module("keyword_normalizer", NORMALIZER_FILE)
semantic_module = load_module("semantic_search", SEMANTIC_FILE)
product_search_module = load_module(
    "product_search",
    PRODUCT_SEARCH_FILE
)


class IntegratedHybridSearch:

    def __init__(self, top_k=20):
        self.parser = parser_module.LLMProductQueryParser()
        self.normalizer = normalizer_module.ProductKeywordNormalizer()

        self.semantic_search = semantic_module.SemanticProductSearch(
            top_k=top_k
        )

        self.product_search = product_search_module.ProductSearch()

    def keyword_match(self, product, keywords):

        if not keywords:
            return True

        text = " ".join([
            product.get("name") or "",
            product.get("description") or "",
            " ".join(product.get("tags", []))
        ]).lower()

        return all(
            keyword.lower() in text
            for keyword in keywords
        )

    def search(self, customer_query):

        filters = self.parser.parse(customer_query)

        keywords = self.normalizer.normalize(
            filters.get("query")
        )

        structured_products = self.product_search.search(
            query=None,
            max_price=filters.get("max_price"),
            category=filters.get("category"),
            in_stock=filters.get("in_stock")
        )

        filtered_products = [
            product
            for product in structured_products
            if self.keyword_match(product, keywords)
        ]

        allowed_urls = {
            product["url"]
            for product in filtered_products
        }

        semantic_matches = self.semantic_search.search(
            customer_query
        )

        results = []

        for match in semantic_matches:

            metadata = match.metadata
            url = metadata.get("url")

            if url in allowed_urls:

                product = next(
                    product
                    for product in filtered_products
                    if product["url"] == url
                )

                results.append({
                    "name": product.get("name"),
                    "price": product.get("price"),
                    "in_stock": product.get("in_stock"),
                    "url": product.get("url"),
                    "score": match.score
                })

        return {
            "query": customer_query,
            "filters": filters,
            "keywords": keywords,
            "results": results
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - INTEGRATED HYBRID SEARCH")
    print("=" * 60)

    searcher = IntegratedHybridSearch(top_k=20)

    queries = [
        "I want oxidized jewellery",
        "I want oxidized earrings under 300 that are available",
        "Show me gold plated jewellery under 500"
    ]

    for query in queries:

        print()
        print("-" * 60)
        print(f"Customer Query: {query}")
        print("-" * 60)

        result = searcher.search(query)

        print()
        print("Filters:")
        print(result["filters"])

        print()
        print(f"Keywords: {result['keywords']}")

        print()
        print(f"Matching Products: {len(result['results'])}")

        for rank, product in enumerate(
            result["results"][:5],
            start=1
        ):

            stock = (
                "In Stock"
                if product["in_stock"]
                else "Out of Stock"
            )

            print()
            print(f"Rank: {rank}")
            print(f"Score: {product['score']:.4f}")
            print(f"Name: {product['name']}")
            print(f"Price: ₹{product['price']}")
            print(f"Stock: {stock}")
            print(f"URL: {product['url']}")

    print()
    print("=" * 60)
    print("INTEGRATED HYBRID SEARCH COMPLETED")
    print("=" * 60)