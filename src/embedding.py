import json
import os
import time
from openai import OpenAI
import chromadb
from dotenv import load_dotenv

CHUNKS_FILE = "data/chunks/eng/chunks.json"
CHROMA_DIR  = "data/chromadb"
COLLECTION  = "uae_labor_law"
EMBED_MODEL = "text-embedding-3-small"
BATCH_SIZE  = 100

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Init ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(
    name=COLLECTION,
    metadata={"hnsw:space": "cosine"}
)

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Call OpenAI embeddings API"""
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]


def run_embedding():
    """Embed chunks and store in ChromaDB."""
    
    # Skip if collection already has data
    if collection.count() > 0:
        print(f"Collection already has {collection.count()} chunks — skipping embedding")
        return

    print("Collection is empty — starting embedding...")

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks")

    total = len(chunks)
    ingested = 0

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]

        texts      = [c["text"] for c in batch]
        metadatas  = [c["metadata"] for c in batch]
        ids        = [c["metadata"]["chunk_id"] for c in batch]
        embeddings = get_embeddings(texts)

        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        ingested += len(batch)
        print(f"  Progress: {ingested}/{total} chunks ingested")
        time.sleep(0.5)

    print(f"\n Done — {collection.count()} chunks stored in ChromaDB")


if __name__ == "__main__":
    run_embedding()