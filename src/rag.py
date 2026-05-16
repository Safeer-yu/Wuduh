import os
from openai import OpenAI
import chromadb
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

CHROMA_DIR  = "data/chromadb"
COLLECTION  = "uae_labor_law"
EMBED_MODEL = "text-embedding-3-small"
TOP_K       = 7 
LLM_MODEL = "gpt-4o"


client = OpenAI(api_key=openai_api_key)
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name=COLLECTION)

def retrieve(query: str) -> list[dict]:
    """Embed the query and retrieve top-k relevant chunks"""
    response = client.embeddings.create(model=EMBED_MODEL, input=[query])
    query_embedding = response.data[0].embedding
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"]
    )
    
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": doc,
            "metadata": meta,
            "score": round(1 - dist, 3)
        })
    
    return chunks


def ask(query: str, history: list[dict] = None) -> dict:
    """Full RAG pipeline with optional conversation memory."""
    if history is None:
        history = []
    
    chunks = retrieve(query)
    
    context = ""
    for i, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        context += f"[{i+1}] {meta['law_name']} — {meta['chunk_id']}\n"
        context += chunk["text"] + "\n\n"
    
    system_prompt = """You are a UAE labor law assistant.
Answer the user's question based strictly on the legal text provided.
Rules:
- Only use information from the provided context
- Always cite the source article number and law name
- If the context doesn't contain enough information, 
  say "I don't have enough information to answer this based on the available legal text"
- Be concise and clear
- Do not give legal advice, only explain what the law states"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {query}"
    })
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0
    )
    
    answer = response.choices[0].message.content
    
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": answer})
    
    return {"answer": answer, "sources": chunks, "history": history}


# if __name__ == "__main__":
#     result = ask("what is the probation period for a new employee?")
#     print(result["answer"])