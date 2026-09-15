import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_module(filename: str, module_name: str):
    path = BASE_DIR / filename

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


extractor_module = load_module(
    "87_smart_order_id_extraction.py",
    "smart_order_id_extraction"
)

handler_module = load_module(
    "85_order_query_handler.py",
    "order_query_handler"
)


class IntegratedOrderTracking:

    def __init__(self):
        self.extractor = extractor_module.SmartOrderIDExtractor()
        self.order_handler = handler_module.OrderQueryHandler()
        self.waiting_for_order_id = False

    def handle(self, message: str) -> dict:

        order_id = self.extractor.extract(message)

        if order_id:
            result = self.order_handler.handle(str(order_id))

            if result.get("status") in {"ORDER_FOUND", "ORDER_NOT_FOUND"}:
                self.waiting_for_order_id = False

            return result

        if self.waiting_for_order_id:
            return {
                "status": "INVALID_ORDER_ID",
                "message": "Please provide a valid Zyra Luxe order ID."
            }

        result = self.order_handler.handle(message)

        if result.get("status") == "ORDER_ID_REQUIRED":
            self.waiting_for_order_id = True

        return result


if __name__ == "__main__":

    tracker = IntegratedOrderTracking()

    print("=" * 55)
    print("INTEGRATED ORDER TRACKING")
    print("=" * 55)

    print("\nConversation 1")

    result = tracker.handle("Where is my order?")
    print(result)

    result = tracker.handle("1177")
    print(result)

    print("\nConversation 2")

    tracker = IntegratedOrderTracking()

    result = tracker.handle("My order number is 1177")
    print(result)

    print("\nConversation 3")

    tracker = IntegratedOrderTracking()

    result = tracker.handle("Please track order 1177")
    print(result)

    print("\nConversation 4")

    tracker = IntegratedOrderTracking()

    result = tracker.handle("My order number is 985")
    print(result)