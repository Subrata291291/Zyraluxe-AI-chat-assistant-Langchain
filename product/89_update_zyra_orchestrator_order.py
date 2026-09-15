import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_module(filename: str, module_name: str):
    path = BASE_DIR / filename

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


router_module = load_module(
    "80_zyra_query_router.py",
    "zyra_query_router"
)

product_module = load_module(
    "76_api_product_response.py",
    "api_product_response"
)

policy_module = load_module(
    "82_policy_rag_integration.py",
    "policy_rag_integration"
)

order_module = load_module(
    "88_integrated_order_tracking.py",
    "integrated_order_tracking"
)


class ZyraAssistantOrchestrator:

    def __init__(self):
        self.router = router_module.ZyraQueryRouter()
        self.product_response = product_module.APIProductResponse()
        self.policy_rag = policy_module.PolicyRAGService()
        self.order_tracking = order_module.IntegratedOrderTracking()

    def handle(self, message: str) -> dict:

        if self.order_tracking.waiting_for_order_id:

            return self.order_tracking.handle(message)

        route = self.router.route(message)

        if route == "PRODUCT":
            return self.product_response.create_response(message)

        if route == "POLICY":
            return self.policy_rag.answer(message)

        if route == "ORDER":
            return self.order_tracking.handle(message)

        if route == "GENERAL":
            return {
                "success": True,
                "route": "GENERAL",
                "answer": "Hello! How can I help you with Zyra Luxe?"
            }

        return {
            "success": False,
            "route": "UNKNOWN",
            "answer": "Sorry, I could not understand your request."
        }

if __name__ == "__main__":

    assistant = ZyraAssistantOrchestrator()

    print("=" * 60)
    print("ZYRA LUXE ASSISTANT - ORDER INTEGRATION")
    print("=" * 60)

    print("\n1. Order without ID")
    print(assistant.handle("Where is my order?"))

    print("\n2. Order ID")
    print(assistant.handle("1177"))

    print("\n3. Natural language order")
    print(assistant.handle("My order number is 1177"))

    print("\n4. Invalid order")
    print(assistant.handle("My order number is 985"))

    print("\n5. Product")
    print(assistant.handle("Show me oxidized earrings under 300"))

    print("\n6. Policy")
    print(assistant.handle("What is your return policy?"))

    print("\n7. General")
    print(assistant.handle("Hello"))