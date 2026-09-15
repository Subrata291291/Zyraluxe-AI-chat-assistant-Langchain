import importlib.util
from pathlib import Path

from fastapi import FastAPI
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


orchestrator_module = load_module(
    "89_update_zyra_orchestrator_order.py",
    "zyra_orchestrator"
)


class ChatRequest(BaseModel):
    message: str


class UnifiedChatResponse:

    def __init__(self):
        self.assistant = (
            orchestrator_module.ZyraAssistantOrchestrator()
        )

    def create_response(self, message: str) -> dict:

        result = self.assistant.handle(message)

        route = result.get("route")

        if route is None:

            if result.get("status", "").startswith("ORDER"):
                route = "ORDER"

            elif "products" in result:
                route = "PRODUCT"

        message = result.get("answer", "")

        if route == "PRODUCT":
            count = result.get("product_count", 0)
            message = f"I found {count} products matching your request."

        response = {
            "success": result.get("success", False),
            "route": route,
            "message": message,
            "data": {}
        }

        if route == "PRODUCT":

            response["data"] = {
                "query": result.get("query"),
                "filters": result.get("filters", {}),
                "product_count": result.get(
                    "product_count", 0
                ),
                "products": result.get("products", [])
            }

        elif route == "POLICY":

            response["data"] = {
                "sources": result.get("sources", [])
            }

        elif route == "ORDER":

            response["data"] = {
                "status": result.get("status"),
                "order_id": result.get("order_id"),
                "order": result.get("order")
            }

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
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:

        return {
            "success": False,
            "route": None,
            "message": "Message cannot be empty.",
            "data": {}
        }

    return chat_response.create_response(message)


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - UNIFIED CHAT RESPONSE")
    print("=" * 60)

    tests = [
        "Hello",
        "Show me oxidized earrings under 300",
        "What is your return policy?",
        "Where is my order?"
    ]

    for test in tests:

        print()
        print(f"User: {test}")

        result = chat_response.create_response(test)

        print(f"Route: {result['route']}")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")