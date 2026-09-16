import importlib.util
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load module: {file_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


ROUTER_FILE = (
    BASE_DIR
    / "80_zyra_query_router.py"
)

PRODUCT_FILE = (
    BASE_DIR
    / "76_api_product_response.py"
)

POLICY_FILE = (
    BASE_DIR
    / "82_policy_rag_integration.py"
)

ORDER_FILE = (
    BASE_DIR
    / "88_integrated_order_tracking.py"
)

GENERAL_FILE = (
    PROJECT_ROOT
    / "ai"
    / "14_general_response.py"
)


router_module = load_module(
    "zyra_query_router",
    ROUTER_FILE
)

product_module = load_module(
    "api_product_response",
    PRODUCT_FILE
)

policy_module = load_module(
    "policy_rag_integration",
    POLICY_FILE
)

order_module = load_module(
    "integrated_order_tracking",
    ORDER_FILE
)

general_module = load_module(
    "general_response",
    GENERAL_FILE
)


class ZyraAssistantOrchestrator:

    def __init__(self):

        self.router = (
            router_module.ZyraQueryRouter()
        )

        self.product_response = (
            product_module.APIProductResponse()
        )

        self.policy_rag = (
            policy_module.PolicyRAGService()
        )

        self.order_tracking = (
            order_module.IntegratedOrderTracking()
        )

        self.general_response = (
            general_module.GeneralResponseGenerator()
        )

    def handle(
        self,
        message: str,
        history: list[dict] | None = None,
        session_id: str | None = None
    ) -> dict:

        if history is None:
            history = []

        if (
            session_id is not None
            and session_id
            in self.order_tracking.waiting_sessions
        ):
            return self.order_tracking.handle(
                message,
                session_id
            )

        route = self.router.route_with_context(
            message,
            history
        )

        if route == "PRODUCT":

            return self.product_response.create_response(
                message,
                history
            )

        if route == "POLICY":

            return self.policy_rag.answer(
                message,
                history
            )

        if route == "ORDER":

            return self.order_tracking.handle(
                message,
                session_id
            )

        if route == "GENERAL":

            result = self.general_response.generate(
                message,
                history
            )

            return {
                "success": result.get(
                    "success",
                    False
                ),
                "route": "GENERAL",
                "answer": result.get(
                    "answer",
                    ""
                )
            }

        return {
            "success": False,
            "route": "UNKNOWN",
            "answer": (
                "Sorry, I could not "
                "understand your request."
            )
        }


if __name__ == "__main__":

    print("=" * 60)
    print(
        "ZYRA LUXE - ORCHESTRATOR TEST"
    )
    print("=" * 60)

    orchestrator = (
        ZyraAssistantOrchestrator()
    )

    history = []

    test_messages = [
        "Hello",
        "How are you?",
        "What can you help me with?",
        "Thanks"
    ]

    for message in test_messages:

        print()
        print("-" * 60)
        print(
            f"Customer: {message}"
        )
        print("-" * 60)

        result = orchestrator.handle(
            message,
            history
        )

        print(
            f"Route: "
            f"{result.get('route')}"
        )

        print(
            f"Answer: "
            f"{result.get('answer')}"
        )

        history.append({
            "role": "user",
            "content": message
        })

        history.append({
            "role": "assistant",
            "content": result.get(
                "answer",
                ""
            )
        })

    print()
    print("=" * 60)
    print(
        "ORCHESTRATOR TEST COMPLETED"
    )
    print("=" * 60)