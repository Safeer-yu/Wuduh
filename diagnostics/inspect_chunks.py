import json

with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Total chunks: {len(chunks)}")

# Distribution by law
from collections import Counter
laws = Counter(c["metadata"]["law_name"] for c in chunks)
for law, count in laws.most_common():
    print(f"  {count:>4} chunks — {law}")

# Check chunk text length
lengths = [len(c["text"].split()) for c in chunks]
print(f"\nChunk word counts:")
print(f"  Min:    {min(lengths)}")
print(f"  Max:    {max(lengths)}")
print(f"  Avg:    {sum(lengths)//len(lengths)}")

# Spot check one chunk
print("\n--- Sample chunk ---")
print(json.dumps(chunks[10], indent=2, ensure_ascii=False))


short_chunks = [(i, c) for i, c in enumerate(chunks) if len(c["text"].split()) < 20]
print(f"Short chunks (< 20 words): {len(short_chunks)}")
for i, c in short_chunks[:10]:
    print(f"\n[{i}] {repr(c['text'])}")
    print(f"     → {c['metadata']['chunk_id']}")

long_chunks = [(i, c) for i, c in enumerate(chunks) if len(c["text"].split()) > 500]
print(f"Long chunks (> 500 words): {len(long_chunks)}")
for i, c in long_chunks:
    print(f"\n[{i}] {len(c['text'].split())} words — {c['metadata']['chunk_id']}")
    print(c["text"][:300])