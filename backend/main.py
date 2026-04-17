from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.rag import chunk_text, add_to_index, query_rag, load_index
from backend.utils import read_pdf


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_index()

chat_history = []

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    text = read_pdf(file.file)
    chunks = chunk_text(text)

    add_to_index(chunks)

    return {"message": "File added to knowledge base"}

@app.get("/chat")
def chat(q: str):
    global chat_history

    answer = query_rag(q, chat_history)

    chat_history.append({"role": "user", "content": q})
    chat_history.append({"role": "assistant", "content": answer})

    return {"answer": answer}