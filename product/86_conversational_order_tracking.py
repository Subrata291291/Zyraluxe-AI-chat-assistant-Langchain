import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ORDER_HANDLER_FILE = (
    PROJECT_ROOT
    / "product"
    / "85_order_query_handler.py"
)


def load_module(name, file_path):

    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


class ConversationalOrderTracking:

    def __init__(self):

        order_module = load_module(
            "order_query_handler",
            ORDER_HANDLER_FILE
        )

        self.order_handler = (
            order_module.OrderQueryHandler()
        )

        self.waiting_for_order_id = False

    def handle(self, message):

        message = message.strip()

        if self.waiting_for_order_id:

            result = self.order_handler.handle(
                message
            )

            if result["status"] == "ORDER_FOUND":

                self.waiting_for_order_id = False

            elif result["status"] == "ORDER_NOT_FOUND":

                self.waiting_for_order_id = False

            return result

        result = self.order_handler.handle(
            message
        )

        if result["status"] == "ORDER_ID_REQUIRED":

            self.waiting_for_order_id = True

        return result


if __name__ == "__main__":

    tracking = ConversationalOrderTracking()

    conversation = [
        "Where is my order?",
        "1177"
    ]

    print("=" * 60)
    print("ZYRA LUXE - CONVERSATIONAL ORDER TRACKING")
    print("=" * 60)

    for message in conversation:

        print()
        print("-" * 60)
        print(f"USER: {message}")
        print("-" * 60)

        result = tracking.handle(message)

        print(f"ASSISTANT: {result['answer']}")
        print(f"STATUS: {result['status']}")

    print()
    print("=" * 60)
    print("CONVERSATIONAL ORDER TEST COMPLETED")
    print("=" * 60)