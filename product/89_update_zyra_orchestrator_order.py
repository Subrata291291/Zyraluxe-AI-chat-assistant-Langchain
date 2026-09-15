import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_module(filename: str, module_name: str):
    path = BASE_DIR / filename

    spec = importlib.util.spec_from_file_location(
        module_name,
        path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load {path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

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


GENERAL_FILE = (
    BASE_DIR.parent
    / "ai"
    / "14_general_response.py"
)

general_spec = importlib.util.spec_from_file_location(
    "general_response",
    GENERAL_FILE
)

if general_spec is None or general_spec.loader is None:
    raise ImportError(
        f"Could not load {GENERAL_FILE}"
    )

general_module = importlib.util.module_from_spec(
    general_spec
)

general_spec.loader.exec_module(
    general_module
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
                "Sorry, I could not understand "
                "your request."
            )
        }


if __name__ == "__main__":

    assistant = ZyraAssistantOrchestrator()

    print("=" * 60)
    print("ZYRA LUXE ASSISTANT - CONTEXT ROUTING")
    print("=" * 60)

    product_history = [
        {
            "role": "user",
            "content": "Show me oxidized earrings"
        },
        {
            "role": "assistant",
            "content": "I found some oxidized earrings."
        }
    ]

    print("\n1. Product follow-up")

    print(
        assistant.handle(
            "Show me more",
            product_history
        )
    )

    policy_history = [
        {
            "role": "user",
            "content": "What is your return policy?"
        },
        {
            "role": "assistant",
            "content": (
                "You can request a return "
                "within 2 hours of delivery."
            )
        }
    ]

    print("\n2. Policy follow-up")

    print(
        assistant.handle(
            "Tell me more",
            policy_history
        )
    )

    print("\n3. Product")

    print(
        assistant.handle(
            "Show me oxidized earrings under 300"
        )
    )

    print("\n4. Policy")

    print(
        assistant.handle(
            "Do you sell my personal information?"
        )
    )

    print("\n5. General")

    print(
        assistant.handle(
            "Hello"
        )
    )