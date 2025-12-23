from fastapi import FastAPI
from pydantic import BaseModel
from app.llm import get_llm
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager

from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore
from app.rag.embeddings import EmbeddingModel
from app.rag.prompt import build_rag_prompt
from app.rag.chunker import chunk_text
from app.rag.loader import load_documents

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting...")
    
    if len(vectorstore.documents) == 0:
        print("Database is empty. Looking for files in 'data/' folder...")
        
        data_path = Path("app/data") 
        
        if data_path.exists() and data_path.is_dir():
            docs = load_documents(data_path)
    
            if docs:
                print(f"Found {len(docs)} chunks in 'data/'. Ingesting now...")
                vectors = embedding_model.embed(docs)
                vectorstore.add(embeddings=vectors, docs=docs)
                print("Ingestion complete!")
            else:
                print("⚠️ 'data/' folder found but no valid .txt/.pdf files inside.")
        else:
            print("⚠️ No 'data/' folder found. Skipping auto-ingestion.")
    else:
        print(f"Loaded {len(vectorstore.documents)} documents from disk.")

    yield 
    print("Server shutting down...")

app = FastAPI(lifespan=lifespan)
embedding_model = EmbeddingModel()
vectorstore = VectorStore(dim=embedding_model.dim)

retriever = Retriever(vectorstore=vectorstore, embedding_model=embedding_model)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

class IngestRequest(BaseModel):
    text: str
    metadata: dict = {}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ingest")
def ingest_document(req: IngestRequest):
    chunks = chunk_text(req.text, chunk_size=80, overlap=20)
    
    if not chunks:
        return {"status": "error", "message": "Text was empty or could not be chunked."}

    print(f"Split text into {len(chunks)} chunks.")

    vectors = embedding_model.embed(chunks)
    
    vectorstore.add(
        embeddings=vectors,
        docs=chunks
    )
    
    return {
        "status": "success", 
        "message": f"Ingested {len(chunks)} chunks successfully."
    }

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    print(f"Searching for: {req.prompt}") 
    
    llm = get_llm()

    context_chunks = retriever.retrieve(req.prompt, k=5)
    
    print(f"Context found ({len(context_chunks)} chunks):")
    for i, c in enumerate(context_chunks):
        print(f"[{i}] {c[:50]}...") 

    rag_prompt = build_rag_prompt(
        context=context_chunks,
        question=req.prompt
    )
    
    def generate():
        for chunk in llm.stream(rag_prompt):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8"
    )