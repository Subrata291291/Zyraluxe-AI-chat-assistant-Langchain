import importlib.util
from pathlib import Path

from fastapi import FastAPI, Header
from pydantic import BaseModel


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


session_manager_path = (
    BASE_DIR.parent / "chatbot" / "15_session_manager.py"
)

session_spec = importlib.util.spec_from_file_location(
    "session_manager",
    session_manager_path
)

session_module = importlib.util.module_from_spec(
    session_spec
)

session_spec.loader.exec_module(
    session_module
)


orchestrator_module = load_module(
    "89_update_zyra_orchestrator_order.py",
    "zyra_orchestrator"
)


class ChatRequest(BaseModel):

    message: str

    session_id: str | None = None


class UnifiedChatResponse:

    def __init__(self):

        self.assistant = (
            orchestrator_module.ZyraAssistantOrchestrator()
        )

        self.session_manager = (
            session_module.SessionManager()
        )

    def create_response(
        self,
        message: str,
        session_id: str | None = None
    ) -> dict:

        if session_id:

            self.session_manager.add_message(
                session_id,
                "user",
                message
            )

        history = []

        if session_id:

            history = (
                self.session_manager.get_recent_history(
                    session_id,
                    limit=6
                )
            )

        print("SESSION:", session_id)
        print("HISTORY:", history)

        result = self.assistant.handle(
            message,
            history,
            session_id
        )

        route = result.get("route")

        if route is None:

            if result.get(
                "status",
                ""
            ).startswith("ORDER"):

                route = "ORDER"

            elif "products" in result:

                route = "PRODUCT"

        response_message = result.get(
            "answer",
            ""
        )

        if route == "PRODUCT":

            count = result.get(
                "product_count",
                0
            )

            response_message = (
                f"I found {count} products "
                "matching your request."
            )

        response = {
            "success": result.get(
                "success",
                False
            ),
            "route": route,
            "message": response_message,
            "data": {}
        }

        if route == "PRODUCT":

            response["data"] = {

                "query": result.get(
                    "query"
                ),

                "filters": result.get(
                    "filters",
                    {}
                ),

                "product_count": result.get(
                    "product_count",
                    0
                ),

                "products": result.get(
                    "products",
                    []
                )
            }

        elif route == "POLICY":

            response["data"] = {

                "sources": result.get(
                    "sources",
                    []
                )
            }

        elif route == "ORDER":

            response["data"] = {

                "status": result.get(
                    "status"
                ),

                "order_id": result.get(
                    "order_id"
                ),

                "order": result.get(
                    "order"
                )
            }

        if session_id:

            products = []

            if route == "PRODUCT":

                products = response["data"].get(
                    "products",
                    []
                )

            self.session_manager.add_message(
                session_id,
                "assistant",
                response["message"],
                products=products
            )

        return response


app = FastAPI(
    title="Zyra Luxe Unified Chat API",
    version="1.0.0"
)


chat_response = UnifiedChatResponse()


@app.get("/")
def root():

    return {
        "success": True,
        "service": "Zyra Luxe Unified Chat API",
        "status": "running"
    }


@app.post("/api/chat")
def chat(
    request: ChatRequest,
    session_id: str | None = Header(
        default=None,
        alias="X-Zyra-Session-ID"
    )
):

    message = request.message.strip()

    active_session_id = (
        session_id
        or request.session_id
    )

    if not message:

        return {
            "success": False,
            "route": None,
            "message": "Message cannot be empty.",
            "data": {}
        }

    return chat_response.create_response(
        message,
        active_session_id
    )


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - CONVERSATIONAL PRODUCT MEMORY TEST")
    print("=" * 60)

    test_session_id = "show-more-test-001"

    tests = [
        "Show me oxidized jewellery",
        "Show me more",
        "Show me more"
    ]

    for number, test in enumerate(
        tests,
        start=1
    ):

        print()
        print("-" * 60)
        print(f"TEST {number}")
        print("-" * 60)

        print()
        print(f"User: {test}")

        result = chat_response.create_response(
            test,
            test_session_id
        )

        print()
        print(f"Route: {result['route']}")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")

        if result["route"] == "PRODUCT":

            products = result["data"].get(
                "products",
                []
            )

            print()
            print(
                f"Products Returned: "
                f"{len(products)}"
            )

            for rank, product in enumerate(
                products,
                start=1
            ):

                print(
                    f"{rank}. "
                    f"{product.get('name')} "
                    f"- ₹{product.get('price')}"
                )

    print()
    print("-" * 60)
    print("FINAL SESSION HISTORY")
    print("-" * 60)

    history = chat_response.session_manager.get_history(
        test_session_id
    )

    for message in history:

        print()
        print(
            f"Role: {message.get('role')}"
        )

        print(
            f"Content: {message.get('content')}"
        )

        if message.get("products"):

            print(
                f"Stored Products: "
                f"{len(message['products'])}"
            )

    print()
    print("=" * 60)
    print("CONVERSATIONAL PRODUCT MEMORY TEST COMPLETED")
    print("=" * 60)