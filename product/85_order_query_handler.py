import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ORDER_API_FILE = (
    PROJECT_ROOT
    / "product"
    / "84_woocommerce_order_api.py"
)


def load_module(name, file_path):

    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


class OrderQueryHandler:

    def __init__(self):

        order_module = load_module(
            "woocommerce_order_api",
            ORDER_API_FILE
        )

        self.order_api = (
            order_module.WooCommerceOrderAPI()
        )

    def extract_order_id(self, query):

        query = query.strip()

        if query.isdigit():
            return int(query)

        return None

    def handle(self, query):

        order_id = self.extract_order_id(query)

        if order_id is None:

            return {
                "success": False,
                "status": "ORDER_ID_REQUIRED",
                "answer": (
                    "Sure. Please provide your "
                    "Zyra Luxe order ID."
                )
            }

        result = self.order_api.get_order(
            order_id
        )

        if not result["success"]:

            return {
                "success": False,
                "status": "ORDER_NOT_FOUND",
                "order_id": order_id,
                "answer": (
                    f"Sorry, I couldn't find an order "
                    f"with ID #{order_id}."
                )
            }

        order = result["order"]

        return {
            "success": True,
            "status": "ORDER_FOUND",
            "order_id": order["id"],
            "answer": (
                f"Your order #{order['id']} is "
                f"{order['status']}."
            ),
            "order": order
        }


if __name__ == "__main__":

    handler = OrderQueryHandler()

    print("=" * 60)
    print("ZYRA LUXE - ORDER QUERY HANDLER")
    print("=" * 60)

    queries = [
        "Where is my order?",
        "1177",
        "985"
    ]

    for query in queries:

        print()
        print("-" * 60)
        print(f"QUERY: {query}")
        print("-" * 60)

        result = handler.handle(query)

        print()
        print("RESULT:")
        print(result)

    print()
    print("=" * 60)
    print("ORDER QUERY HANDLER TEST COMPLETED")
    print("=" * 60)