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
        "personal information",
        "personal data",
        "sell my data",
        "sell my information",
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

    FOLLOW_UP_PHRASES = [
        "show me more",
        "show more",
        "tell me more",
        "more",
        "more options",
        "anything else",
        "what else",
        "another one",
        "another",
        "more like this"
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

    def is_follow_up(self, query):

        normalized_query = self.normalize(query)

        return normalized_query in self.FOLLOW_UP_PHRASES

    def route_with_context(
        self,
        query,
        history=None
    ):

        if history is None:
            history = []

        current_route = self.route(query)

        if current_route != "GENERAL":
            return current_route

        if not self.is_follow_up(query):
            return "GENERAL"

        for message in reversed(history):

            if message.get("role") != "user":
                continue

            previous_query = message.get("content", "")
            previous_route = self.route(previous_query)

            if previous_route != "GENERAL":
                return previous_route

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
        "Do you sell my personal information?",
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
    print("-" * 60)
    print("CONTEXT-AWARE ROUTING TEST")
    print("-" * 60)

    history = [
        {
            "role": "user",
            "content": "Show me oxidized earrings"
        },
        {
            "role": "assistant",
            "content": "I found some oxidized earrings."
        }
    ]

    test_query = "Show me more"

    print()
    print(f"Previous : {history[0]['content']}")
    print(f"Current  : {test_query}")
    print(f"Route    : {router.route_with_context(test_query, history)}")

    print()
    print("-" * 60)
    print("POLICY FOLLOW-UP TEST")
    print("-" * 60)

    history = [
        {
            "role": "user",
            "content": "What is your return policy?"
        },
        {
            "role": "assistant",
            "content": "You can request a return within 2 hours of delivery."
        }
    ]

    test_query = "Tell me more"

    print()
    print(f"Previous : {history[0]['content']}")
    print(f"Current  : {test_query}")
    print(f"Route    : {router.route_with_context(test_query, history)}")

    print()
    print("=" * 60)
    print("QUERY ROUTING COMPLETED")
    print("=" * 60)