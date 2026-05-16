from src.rag import ask
# run this in a separate test file or python console
from src.rag import retrieve
results = retrieve("termination warning period employer employee")
for r in results:
    print(f"Score: {r['score']} | {r['metadata']['chunk_id']}")
    print(r['text'][:150])
    print()