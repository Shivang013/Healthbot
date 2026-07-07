from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag import ask

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    history: list = []


@app.get("/")
def home():
    return {"message": "Backend Working"}


@app.post("/chat")
def chat(req: ChatRequest):

    answer = ask(req.question, req.history)

    return {
        "answer": answer
    }