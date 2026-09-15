from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="Zyra Luxe AI Assistant",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str


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


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    return ChatResponse(
        session_id=request.session_id,
        answer=f"Received message: {request.message}"
    )


if __name__ == "__main__":

    import uvicorn
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )