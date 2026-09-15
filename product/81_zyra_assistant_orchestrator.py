import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ROUTER_FILE = (
    PROJECT_ROOT
    / "product"
    / "80_zyra_query_router.py"
)

PRODUCT_FILE = (
    PROJECT_ROOT
    / "product"
    / "76_api_product_response.py"
)

ANSWER_GENERATOR_FILE = (
    PROJECT_ROOT
    / "answer_generator.py"
)


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


class ZyraLuxeAssistant:

    def __init__(self):

        router_module = load_module(
            "zyra_query_router",
            ROUTER_FILE
        )

        product_module = load_module(
            "api_product_response",
            PRODUCT_FILE
        )

        self.router = router_module.ZyraQueryRouter()

        self.product_service = (
            product_module.APIProductResponse()
        )

        self.answer_generator = None

        if ANSWER_GENERATOR_FILE.exists():
            self.answer_generator = load_module(
                "answer_generator",
                ANSWER_GENERATOR_FILE
            )

    def handle(self, customer_query):

        route = self.router.route(
            customer_query
        )

        print()
        print(f"QUERY: {customer_query}")
        print(f"ROUTE: {route}")

        if route == "PRODUCT":
            return self.handle_product(
                customer_query
            )

        if route == "POLICY":
            return self.handle_policy(
                customer_query
            )

        if route == "ORDER":
            return self.handle_order(
                customer_query
            )

        return self.handle_general(
            customer_query
        )

    def handle_product(self, query):

        response = self.product_service.create_response(
            query
        )

        return {
            "route": "PRODUCT",
            "response": response
        }

    def handle_policy(self, query):

        if self.answer_generator is None:

            return {
                "route": "POLICY",
                "answer": (
                    "The policy knowledge system "
                    "is currently unavailable."
                )
            }

        return {
            "route": "POLICY",
            "answer": (
                "Policy RAG integration will use "
                "the existing knowledge retrieval "
                "and answer generation components."
            )
        }

    def handle_order(self, query):

        return {
            "route": "ORDER",
            "answer": (
                "Order tracking will be connected "
                "to the live order system."
            )
        }

    def handle_general(self, query):

        if self.answer_generator is None:

            return {
                "route": "GENERAL",
                "answer": (
                    "Hello! How can I help you "
                    "with Zyra Luxe?"
                )
            }

        return {
            "route": "GENERAL",
            "answer": (
                "General conversation will use "
                "the existing LLM answer generator."
            )
        }


if __name__ == "__main__":

    assistant = ZyraLuxeAssistant()

    test_queries = [
        "I want oxidized jewellery",
        "What is your return policy?",
        "Where is my order?",
        "Hello"
    ]

    print("=" * 60)
    print("ZYRA LUXE - ASSISTANT ORCHESTRATOR")
    print("=" * 60)

    for query in test_queries:

        result = assistant.handle(query)

        print()
        print("RESULT:")
        print(result)

        print()
        print("-" * 60)

    print()
    print("ORCHESTRATION TEST COMPLETED")