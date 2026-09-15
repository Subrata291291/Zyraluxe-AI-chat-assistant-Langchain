import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_module(filename: str, module_name: str):
    path = BASE_DIR / filename

    spec = importlib.util.spec_from_file_location(
        module_name,
        path
    )

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
        self.waiting_sessions = set()

    def handle(
        self,
        message: str,
        session_id: str | None = None
    ) -> dict:

        order_id = self.extractor.extract(message)

        is_waiting = (
            session_id is not None
            and session_id in self.waiting_sessions
        )

        if order_id:

            result = self.order_handler.handle(
                str(order_id)
            )

            if result.get("status") == "ORDER_FOUND":

                if session_id:
                    self.waiting_sessions.discard(
                        session_id
                    )

            elif result.get("status") == "ORDER_NOT_FOUND":

                if session_id:
                    self.waiting_sessions.add(
                        session_id
                    )

            return result

        if is_waiting:

            return {
                "success": False,
                "status": "INVALID_ORDER_ID",
                "message": "Please provide a valid Zyra Luxe order ID."
            }

        result = self.order_handler.handle(message)

        if result.get("status") == "ORDER_ID_REQUIRED":

            if session_id:
                self.waiting_sessions.add(
                    session_id
                )

        return result


if __name__ == "__main__":

    tracker = IntegratedOrderTracking()

    print("=" * 55)
    print("INTEGRATED ORDER TRACKING")
    print("=" * 55)

    session_1 = "user-001"

    print("\nConversation 1")

    result = tracker.handle(
        "Where is my order?",
        session_1
    )
    print(result)

    result = tracker.handle(
        "1177",
        session_1
    )
    print(result)

    print("\nConversation 2")

    session_2 = "user-002"

    result = tracker.handle(
        "My order number is 1177",
        session_2
    )
    print(result)

    print("\nConversation 3")

    session_3 = "user-003"

    result = tracker.handle(
        "Please track order 1177",
        session_3
    )
    print(result)

    print("\nConversation 4")

    session_4 = "user-004"

    result = tracker.handle(
        "My order number is 985",
        session_4
    )
    print(result)

    print("\nConversation 5")

    result = tracker.handle(
        "Show me earrings",
        session_1
    )
    print(result)