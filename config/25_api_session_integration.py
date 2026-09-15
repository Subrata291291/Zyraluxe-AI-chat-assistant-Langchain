from fastapi import FastAPI
from pydantic import BaseModel

from datetime import datetime


app = FastAPI(
    title="Zyra Luxe AI Assistant",
    version="1.0"
)


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def create_session(
        self,
        session_id: str
    ):

        if session_id not in self.sessions:
            self.sessions[session_id] = []

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):

        self.create_session(session_id)

        self.sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_history(
        self,
        session_id: str
    ):

        return self.sessions.get(
            session_id,
            []
        )


class ChatRequest(BaseModel):

    session_id: str
    message: str


class ChatResponse(BaseModel):

    session_id: str
    answer: str
    history: list[dict]


session_manager = SessionManager()


@app.get("/")
def root():

    return {
        "message": "Zyra Luxe AI Assistant API"
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
def chat(request: ChatRequest):

    session_manager.add_message(
        request.session_id,
        "user",
        request.message
    )

    answer = (
        f"Received your message: "
        f"{request.message}"
    )

    session_manager.add_message(
        request.session_id,
        "assistant",
        answer
    )

    history = session_manager.get_history(
        request.session_id
    )

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        history=history
    )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )