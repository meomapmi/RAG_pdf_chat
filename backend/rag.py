import faiss
import pickle
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

index = None
documents = []
DATA_PATH = "data"

def save_index():
    global index, documents
    if index is not None:
        faiss.write_index(index, f"{DATA_PATH}/index.faiss")
        with open(f"{DATA_PATH}/docs.pkl", "wb") as f:
            pickle.dump(documents, f)

def load_index():
    global index, documents
    try:
        index = faiss.read_index(f"{DATA_PATH}/index.faiss")
        with open(f"{DATA_PATH}/docs.pkl", "rb") as f:
            documents = pickle.load(f)
        print("Index loaded")
    except:
        print("No index found")

def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)

    return chunks

# def build_index(chunks):
#     global index, documents
#     embeddings = embed_model.encode(chunks)

#     dim = embeddings.shape[1]
#     index = faiss.IndexFlatL2(dim)
#     index.add(embeddings)

#     documents = chunks
#     save_index()

def add_to_index(chunks):
    global index, documents

    embeddings = embed_model.encode(chunks)

    if index is None:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)

    index.add(embeddings)
    documents.extend(chunks)

    save_index()


def query_rag(question, chat_history, top_k=5):
    global index, documents

    if index is None:
        return "Bạn chưa upload tài liệu."

    q_emb = embed_model.encode([question])
    D, I = index.search(q_emb, top_k)

    context = "\n".join([documents[i] for i in I[0]])

    history_text = ""
    for h in chat_history[-5:]:
        history_text += f"{h['role']}: {h['content']}\n"

    prompt = f"""
You are a helpful assistant.

Chat history:
{history_text}

Context:
{context}

Question: {question}
"""

    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )

    return response.output_text