import re


class ZyraQueryRouter:

    PRODUCT_KEYWORDS = [
        "product",
        "products",
        "earring",
        "earrings",
        "jhumka",
        "necklace",
        "bangle",
        "bangles",
        "jewellery",
        "jewelry",
        "ring",
        "rings",
        "set",
        "combo",
        "oxidized",
        "gold plated",
        "silver",
        "buy",
        "price",
        "under",
        "below",
        "available",
        "in stock"
    ]

    POLICY_KEYWORDS = [
        "return",
        "returns",
        "refund",
        "refunds",
        "exchange",
        "exchanges",
        "return policy",
        "privacy",
        "privacy policy",
        "shipping policy",
        "delivery policy",
        "cancel",
        "cancellation",
        "damaged",
        "defective"
    ]

    ORDER_KEYWORDS = [
        "order",
        "orders",
        "track my order",
        "track order",
        "order status",
        "where is my order",
        "delivery status",
        "shipment",
        "tracking"
    ]

    def normalize(self, query):
        return re.sub(
            r"\s+",
            " ",
            query.lower().strip()
        )

    def route(self, query):

        normalized_query = self.normalize(query)

        if any(
            keyword in normalized_query
            for keyword in self.ORDER_KEYWORDS
        ):
            return "ORDER"

        if any(
            keyword in normalized_query
            for keyword in self.POLICY_KEYWORDS
        ):
            return "POLICY"

        if any(
            keyword in normalized_query
            for keyword in self.PRODUCT_KEYWORDS
        ):
            return "PRODUCT"

        return "GENERAL"


if __name__ == "__main__":

    router = ZyraQueryRouter()

    queries = [
        "I want oxidized jewellery",
        "Show me earrings under 300",
        "What is your return policy?",
        "Can I get a refund?",
        "Can I exchange a damaged product?",
        "Where is my order?",
        "Track my order",
        "Hello",
        "Tell me about your company"
    ]

    print("=" * 60)
    print("ZYRA LUXE - QUERY ROUTER")
    print("=" * 60)

    for query in queries:

        route = router.route(query)

        print()
        print(f"Query : {query}")
        print(f"Route : {route}")

    print()
    print("=" * 60)
    print("QUERY ROUTING COMPLETED")
    print("=" * 60)