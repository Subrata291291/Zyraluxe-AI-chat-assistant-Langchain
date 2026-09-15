import re


class ProductKeywordNormalizer:

    STOP_WORDS = {
        "jewellery",
        "jewelry",
        "product",
        "products",
        "item",
        "items",
        "show",
        "want",
        "need",
        "looking",
        "for",
        "something",
        "please",
        "me",
        "i",
        "a",
        "an",
        "the",
        "some"
    }

    def normalize(self, query):

        if not query:
            return []

        words = re.findall(r"[a-zA-Z]+", query.lower())

        keywords = [
            word
            for word in words
            if word not in self.STOP_WORDS
        ]

        return list(dict.fromkeys(keywords))


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT KEYWORD NORMALIZER")
    print("=" * 60)

    normalizer = ProductKeywordNormalizer()

    queries = [
        "oxidized jewellery",
        "gold plated jewellery",
        "beautiful oxidized earrings",
        "wedding jewellery",
        "stylish products for women"
    ]

    for query in queries:

        keywords = normalizer.normalize(query)

        print()
        print(f"Query: {query}")
        print(f"Keywords: {keywords}")

    print()
    print("=" * 60)
    print("KEYWORD NORMALIZATION COMPLETED")
    print("=" * 60)