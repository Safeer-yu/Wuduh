import os
from openai import OpenAI
import chromadb
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

CHROMA_DIR  = "data/chromadb"
COLLECTION  = "uae_labor_law"
EMBED_MODEL = "text-embedding-3-small"


client = OpenAI(api_key=openai_api_key)
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name=COLLECTION)

print(f"Total chunks in collection: {collection.count()}")

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(model=EMBED_MODEL, input=[text])
    return response.data[0].embedding

def search(query: str, n: int = 3):
    results = collection.query(
        query_embeddings=[get_embedding(query)],
        n_results=n,
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"\n{'='*60}")
    print(f"Query: '{query}'")
    print(f"{'='*60}")
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        score = 1 - dist  # cosine similarity, higher = better
        print(f"\n  Result {i+1} | score: {score:.3f} | {meta['chunk_id']}")
        print(f"  Law: {meta['law_name']}")
        print(f"  Text: {doc[:250]}...")

# ── Test queries ─────────────────────────────────────────
search("what is the end of service gratuity entitlement?")
search("how many sick days is an employee entitled to?")
search("what are the working hours per week?")
search("can an employer terminate a worker without notice?")
search("what is the probation period for a new employee?")