import re


class SmartOrderIDExtractor:

    def extract(self, message):

        message = message.strip()

        patterns = [
            r"order\s*(?:number|no|id)\s*(?:is|:)?\s*#?\s*(\d+)",
            r"order\s*#?\s*(\d+)",
            r"#\s*(\d+)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                message,
                re.IGNORECASE
            )

            if match:
                return int(match.group(1))

        if message.isdigit():
            return int(message)

        return None

if __name__ == "__main__":

    extractor = SmartOrderIDExtractor()

    test_messages = [
        "Where is my order?",
        "My order number is 1177",
        "Can you check order #1177?",
        "Please track order 1177",
        "#1177",
        "1177",
        "I need help with my order 985",
    ]

    print("=" * 60)
    print("ZYRA LUXE - SMART ORDER ID EXTRACTION")
    print("=" * 60)

    for message in test_messages:

        order_id = extractor.extract(message)

        print()
        print(f"Message: {message}")
        print(f"Order ID: {order_id}")

    print()
    print("=" * 60)
    print("ORDER ID EXTRACTION TEST COMPLETED")
    print("=" * 60)