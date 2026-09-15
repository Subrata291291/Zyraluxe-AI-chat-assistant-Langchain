def route_query(query: str) -> str:

    query = query.lower()

    order_keywords = [
        "order",
        "track",
        "tracking",
        "delivery status",
        "where is my",
    ]

    policy_keywords = [
        "return",
        "refund",
        "exchange",
        "privacy",
        "personal information",
        "data",
        "shipping policy",
        "policy",
    ]

    product_keywords = [
        "buy",
        "price",
        "cost",
        "available",
        "in stock",
        "earring",
        "necklace",
        "bracelet",
        "ring",
        "jewellery",
        "jewelry",
        "product",
    ]

    if any(
        keyword in query
        for keyword in order_keywords
    ):
        return "order"

    if any(
        keyword in query
        for keyword in policy_keywords
    ):
        return "policy"

    if any(
        keyword in query
        for keyword in product_keywords
    ):
        return "product"

    return "general"


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - QUERY ROUTER")
    print("=" * 60)

    print()
    print("Type 'exit' to stop.")

    while True:

        query = input(
            "\nQuery: "
        ).strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        route = route_query(query)

        print(
            f"Route: {route}"
        )

    print()
    print("Router stopped.")