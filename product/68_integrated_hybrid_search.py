import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


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


PARSER_FILE = (
    PROJECT_ROOT
    / "product"
    / "59_llm_product_query_parser.py"
)

NORMALIZER_FILE = (
    PROJECT_ROOT
    / "product"
    / "67_product_keyword_normalizer.py"
)

SEMANTIC_FILE = (
    PROJECT_ROOT
    / "product"
    / "64_semantic_product_search.py"
)

PRODUCT_API_FILE = (
    PROJECT_ROOT
    / "product"
    / "92_woocommerce_product_api.py"
)


parser_module = load_module(
    "llm_parser",
    PARSER_FILE
)

normalizer_module = load_module(
    "keyword_normalizer",
    NORMALIZER_FILE
)

semantic_module = load_module(
    "semantic_search",
    SEMANTIC_FILE
)

product_api_module = load_module(
    "woocommerce_product_api",
    PRODUCT_API_FILE
)


class IntegratedHybridSearch:

    def __init__(self, top_k=20):

        self.top_k = top_k

        self.parser = (
            parser_module.LLMProductQueryParser()
        )

        self.normalizer = (
            normalizer_module.ProductKeywordNormalizer()
        )

        self.semantic_search = (
            semantic_module.SemanticProductSearch(
                top_k=max(
                    top_k,
                    50
                )
            )
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

        return [
            self.normalize_product(product)
            for product in all_products
        ]

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

        description = product.get(
            "short_description"
        ) or product.get(
            "description"
        ) or ""

        return {
            "id": product.get("id"),
            "name": product.get("name", ""),
            "price": self.parse_price(
                product.get("price")
            ),
            "in_stock": (
                product.get("stock_status")
                == "instock"
            ),
            "url": product.get(
                "permalink",
                ""
            ),
            "description": description,
            "categories": categories,
            "tags": tags
        }

    def parse_price(
        self,
        price
    ):

        if price in (
            None,
            ""
        ):
            return None

        try:
            return float(price)
        except (
            TypeError,
            ValueError
        ):
            return None

    def keyword_match(
        self,
        product,
        keywords
    ):

        if not keywords:
            return True

        text = " ".join([
            product.get("name") or "",
            product.get("description") or "",
            " ".join(
                product.get(
                    "categories",
                    []
                )
            ),
            " ".join(
                product.get(
                    "tags",
                    []
                )
            )
        ]).lower()

        return all(
            keyword.lower() in text
            for keyword in keywords
        )

    def apply_filters(
        self,
        products,
        filters
    ):

        results = []

        min_price = filters.get(
            "min_price"
        )

        max_price = filters.get(
            "max_price"
        )

        category = filters.get(
            "category"
        )

        in_stock = filters.get(
            "in_stock"
        )

        for product in products:

            price = product.get(
                "price"
            )

            if (
                min_price is not None
                and (
                    price is None
                    or price < min_price
                )
            ):
                continue

            if (
                max_price is not None
                and (
                    price is None
                    or price > max_price
                )
            ):
                continue

            if category:

                category_text = " ".join(
                    product.get(
                        "categories",
                        []
                    )
                ).lower()

                if (
                    category.lower()
                    not in category_text
                ):
                    continue

            if (
                in_stock is True
                and not product.get(
                    "in_stock"
                )
            ):
                continue

            results.append(
                product
            )

        return results

    def search(
        self,
        customer_query
    ):

        filters = self.parser.parse(
            customer_query
        )

        keywords = self.normalizer.normalize(
            filters.get("query")
        )

        live_products = (
            self.get_live_products()
        )

        filtered_products = self.apply_filters(
            live_products,
            filters
        )

        filtered_products = [
            product
            for product in filtered_products
            if self.keyword_match(
                product,
                keywords
            )
        ]

        if not filtered_products:

            return {
                "query": customer_query,
                "filters": filters,
                "keywords": keywords,
                "results": []
            }

        product_map = {
            product["url"]: product
            for product in filtered_products
            if product.get("url")
        }

        results = []

        seen_urls = set()

        semantic_matches = (
            self.semantic_search.search(
                customer_query
            )
        )

        for match in semantic_matches:

            metadata = match.metadata

            url = metadata.get(
                "url"
            )

            if url not in product_map:
                continue

            if url in seen_urls:
                continue

            product = product_map.get(
                url
            )

            if not product:
                continue

            seen_urls.add(url)

            results.append({
                "name": product.get(
                    "name"
                ),
                "price": product.get(
                    "price"
                ),
                "in_stock": product.get(
                    "in_stock"
                ),
                "url": product.get(
                    "url"
                ),
                "score": float(
                    match.score
                )
            })

            if len(results) >= self.top_k:
                break

        semantic_urls = set(
            seen_urls
        )

        remaining_products = [
            product
            for product in filtered_products
            if product.get("url")
            not in semantic_urls
        ]

        for product in remaining_products:

            results.append({
                "name": product.get(
                    "name"
                ),
                "price": product.get(
                    "price"
                ),
                "in_stock": product.get(
                    "in_stock"
                ),
                "url": product.get(
                    "url"
                ),
                "score": 0.0
            })

            if len(results) >= self.top_k:
                break

        return {
            "query": customer_query,
            "filters": filters,
            "keywords": keywords,
            "results": results
        }


if __name__ == "__main__":

    print("=" * 60)
    print(
        "ZYRA LUXE - LIVE WOOCOMMERCE HYBRID SEARCH"
    )
    print("=" * 60)

    searcher = IntegratedHybridSearch(
        top_k=35
    )

    print()
    print("Fetching live WooCommerce products...")

    live_products = (
        searcher.get_live_products()
    )

    print(
        f"Live products found: "
        f"{len(live_products)}"
    )

    queries = [
        "I want oxidized jewellery",
        "I want oxidized earrings under 300 that are available",
        "Show me gold plated jewellery under 500"
    ]

    for query in queries:

        print()
        print("-" * 60)
        print(
            f"Customer Query: {query}"
        )
        print("-" * 60)

        result = searcher.search(
            query
        )

        print()
        print("Filters:")
        print(
            result["filters"]
        )

        print()
        print(
            f"Keywords: "
            f"{result['keywords']}"
        )

        print()
        print(
            f"Matching Products: "
            f"{len(result['results'])}"
        )

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
            print(
                f"Rank: {rank}"
            )

            print(
                f"Score: "
                f"{product['score']:.4f}"
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
                f"{stock}"
            )

            print(
                f"URL: "
                f"{product['url']}"
            )

    print()
    print("=" * 60)
    print(
        "LIVE WOOCOMMERCE HYBRID SEARCH COMPLETED"
    )
    print("=" * 60)