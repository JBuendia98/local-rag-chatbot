from fastapi import FastAPI
from pydantic import BaseModel
from app.llm import get_llm

app = FastAPI()

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
