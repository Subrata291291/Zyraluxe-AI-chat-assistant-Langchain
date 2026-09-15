import re


class ProductQueryParser:

    def parse(self, query):

        query_lower = query.lower()

        filters = {
            "query": None,
            "max_price": None,
            "category": None,
            "in_stock": None
        }

        categories = [
            "earrings",
            "necklace",
            "bangles",
            "combo"
        ]

        for category in categories:

            if category in query_lower:
                filters["category"] = category
                break

        price_match = re.search(
            r"(?:under|below|less than|upto|up to)\s*[₹rs.]?\s*(\d+)",
            query_lower
        )

        if price_match:
            filters["max_price"] = float(
                price_match.group(1)
            )

        stock_words = [
            "available",
            "in stock",
            "instock"
        ]

        if any(word in query_lower for word in stock_words):
            filters["in_stock"] = True

        if "out of stock" in query_lower:
            filters["in_stock"] = False

        return filters


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT QUERY PARSER")
    print("=" * 60)

    parser = ProductQueryParser()

    queries = [
        "Show me earrings under ₹300 that are available",
        "I want necklace below 500",
        "Show me bangles upto ₹200",
        "I want earrings that are in stock",
        "Show me out of stock necklace"
    ]

    for query in queries:

        result = parser.parse(query)

        print()
        print("-" * 60)
        print(f"Query: {query}")
        print(f"Filters: {result}")

    print()
    print("=" * 60)
    print("PRODUCT QUERY PARSER CHECK COMPLETED")
    print("=" * 60)