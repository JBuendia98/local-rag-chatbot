from fastapi import FastAPI
from pydantic import BaseModel
from app.llm import get_llm
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    llm = get_llm()
    response = llm.invoke(req.prompt)
    return {"response": response}

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    llm = get_llm()

    def generate():
        for chunk in llm.stream(req.prompt):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8"
    )