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


app = FastAPI(
    title="Zyra Luxe AI Assistant",
    description="Unified chat API for Zyra Luxe",
    version="1.0.0"
)


assistant = orchestrator_module.ZyraAssistantOrchestrator()


@app.get("/")
def root():

    return {
        "success": True,
        "service": "Zyra Luxe AI Assistant",
        "status": "running"
    }


@app.post("/api/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:
        return {
            "success": False,
            "error": "Message cannot be empty."
        }

    result = assistant.handle(message)

    return result