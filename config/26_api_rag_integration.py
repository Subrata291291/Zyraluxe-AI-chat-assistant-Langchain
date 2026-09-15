import importlib.util
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


BASE_DIR = Path(__file__).parent

CONFIG_FILE = BASE_DIR / "18_config.py"
FACTORY_FILE = BASE_DIR / "22_rag_service_factory.py"
PIPELINE_FILE = BASE_DIR / "23_rag_pipeline.py"

SESSION_FILE = (
    BASE_DIR.parent
    / "chatbot"
    / "15_session_manager.py"
)


def load_module(
    name: str,
    file_path: Path
):

    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load module: {file_path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(module)

    return module


config = load_module(
    "zyra_config",
    CONFIG_FILE
)

factory = load_module(
    "zyra_factory",
    FACTORY_FILE
)

pipeline = load_module(
    "zyra_pipeline",
    PIPELINE_FILE
)

session_module = load_module(
    "zyra_session",
    SESSION_FILE
)


components = factory.create_components(
    config
)

session_manager = (
    session_module.SessionManager()
)


app = FastAPI(
    title="Zyra Luxe AI Assistant",
    version="2.0"
)


class ChatRequest(BaseModel):

    session_id: str
    message: str


class Source(BaseModel):

    title: str | None = None
    url: str | None = None
    score: float | None = None


class ChatResponse(BaseModel):

    session_id: str
    answer: str
    sources: list[Source]
    history: list[dict]


@app.get("/")
def root():

    return {
        "message": "Zyra Luxe AI Assistant API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest
):

    session_manager.add_message(
        request.session_id,
        "user",
        request.message
    )

    result = pipeline.run_pipeline(
        request.message,
        components,
        config
    )

    answer = result["answer"]

    session_manager.add_message(
        request.session_id,
        "assistant",
        answer
    )

    history = session_manager.get_history(
        request.session_id
    )

    sources = [
        Source(
            title=source.get("title"),
            url=source.get("url"),
            score=source.get("score")
        )
        for source in result["sources"]
    ]

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        sources=sources,
        history=history
    )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT
    )