import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


ROUTER_FILE = PROJECT_ROOT / "product" / "80_zyra_query_router.py"
PRODUCT_FILE = PROJECT_ROOT / "product" / "76_api_product_response.py"
POLICY_FILE = PROJECT_ROOT / "product" / "82_policy_rag_integration.py"


def load_module(name, file_path):

    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


class ZyraAssistantOrchestrator:

    def __init__(self):

        router_module = load_module(
            "zyra_query_router",
            ROUTER_FILE
        )

        product_module = load_module(
            "api_product_response",
            PRODUCT_FILE
        )

        policy_module = load_module(
            "policy_rag",
            POLICY_FILE
        )

        self.router = router_module.ZyraQueryRouter()

        self.product_service = (
            product_module.APIProductResponse()
        )

        self.policy_service = (
            policy_module.PolicyRAGService()
        )

    def handle_product(self, query):

        return self.product_service.create_response(
            query
        )

    def handle_policy(self, query):

        return self.policy_service.answer(
            query
        )

    def handle_order(self, query):

        return {
            "route": "ORDER",
            "answer": (
                "Order tracking will be connected "
                "to the live order system."
            )
        }

    def handle_general(self, query):

        return {
            "route": "GENERAL",
            "answer": (
                "Hello! How can I help you "
                "with Zyra Luxe?"
            )
        }

    def handle(self, query):

        route = self.router.route(query)

        if route == "PRODUCT":

            return {
                "route": route,
                "response": self.handle_product(query)
            }

        if route == "POLICY":

            return self.handle_policy(query)

        if route == "ORDER":

            return self.handle_order(query)

        return self.handle_general(query)


if __name__ == "__main__":

    assistant = ZyraAssistantOrchestrator()

    queries = [
        "I want oxidized jewellery",
        "What is your return policy?",
        "Can I get a refund?",
        "What is your privacy policy?",
        "Where is my order?",
        "Hello"
    ]

    print("=" * 60)
    print("ZYRA LUXE - UPDATED ASSISTANT ORCHESTRATOR")
    print("=" * 60)

    for query in queries:

        print()
        print("-" * 60)
        print(f"QUERY: {query}")
        print("-" * 60)

        result = assistant.handle(query)

        print()
        print("RESULT:")
        print(result)

    print()
    print("=" * 60)
    print("UPDATED ORCHESTRATION TEST COMPLETED")
    print("=" * 60)