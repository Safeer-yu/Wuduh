import json
import os
from pathlib import Path
import re
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class LawChunk:
    text: str
    metadata: dict

def split_into_articles(raw_text: str) -> list[tuple[str, str]]:
    # '^' with re.MULTILINE ensures we only match Article at line start
    pattern = r'(?=^Article\s*\(?\d+\)?)' 
    parts = re.split(pattern, raw_text, flags=re.MULTILINE)
    
    articles = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        match = re.match(r'Article\s*\(?\s*(\d+)\s*\)?', part) # article number
        if match:
            articles.append((match.group(1), part))
    return articles


def chunk_article(article_num: str, article_text: str,
                  max_tokens: int = 600):  
    """
    Only split if article is very long. Most articles should stay whole.
    """
    if len(article_text) / 4 <= max_tokens:
        return [article_text]
    
    # Split only on top-level numbered sections that start on their own line
    # Require the number to be at the start of a line after a blank line
    section_pattern = r'(?=\n\n\s*\d+\.)'  # double newline before number
    sections = re.split(section_pattern, article_text)
    
    # If splitting didn't help much, just return whole article
    if len(sections) <= 1:
        return [article_text]
    
    chunks = []
    header_match = re.match(r'(Article\s*\(?\d+\)?[^\n]*\n[^\n]*)', article_text)
    header = header_match.group(1) if header_match else ""
    
    for i, section in enumerate(sections):
        section = section.strip()
        if not section or len(section.split()) < 20:
            continue
        if i > 0 and header:
            chunk_text = f"{header}\n{section}"
        else:
            chunk_text = section
        chunks.append(chunk_text)
    
    return chunks if chunks else [article_text]


def extract_clean_text(raw_text: str) -> str:
    # Cut off annexures/schedules — they appear after the signature
    cutoff_patterns = [
        "SCHEDULE NO.",
        "ANNEX NO.",
        "Original is signed by His Highness",
        "----------------------------- Dated:"
    ]
    for pattern in cutoff_patterns:
        idx = raw_text.find(pattern)
        if idx != -1:
            raw_text = raw_text[:idx]
    return raw_text

def build_chunks(raw_text: str, law_name: str, version_year: int,
                 language: str, source_file: str) -> list[LawChunk]:
    
    raw_text = extract_clean_text(raw_text)
    articles = split_into_articles(raw_text)
    all_chunks = []
    
    law_id = source_file.replace(".txt", "")[:20].replace(" ", "_").lower()
    
    # Track seen IDs within this file to catch duplicates
    seen_ids = {}

    for article_num, article_text in articles:
        sub_chunks = chunk_article(article_num, article_text)
        
        for i, chunk_text in enumerate(sub_chunks):
            section = str(i + 1) if len(sub_chunks) > 1 else None
            
            base_id = f"{law_id}_art{article_num}_{'s'+str(i+1) if section else 'full'}_{language}_{version_year}"
            
            # If ID already seen, append a counter to make it unique
            if base_id in seen_ids:
                seen_ids[base_id] += 1
                chunk_id = f"{base_id}_dup{seen_ids[base_id]}"
            else:
                seen_ids[base_id] = 0
                chunk_id = base_id

            metadata = {
                "article_number": article_num,
                "law_name": law_name,
                "version_year": version_year,
                "language": language,
                "source_file": source_file,
                "section": section,
                "chunk_id": chunk_id
            }
            all_chunks.append(LawChunk(text=chunk_text, metadata=metadata))
    
    return all_chunks


# Configure files
TEXT_DIR = "data/processed/eng"   
OUTPUT_FILE = "data/chunks/eng/chunks.json"

FILE_METADATA = {
    "Cabinet Decision No. 106 of 2022 pertaining to the executive regulations of Federal Decree Law No. 9 of 2022.txt": {
        "law_name": "Cabinet Decision No. 106 of 2022 - Executive Regulations of Federal Decree Law No. 9 of 2022",
        "version_year": 2022,
        "language": "en"
    },
    "Cabinet Resolution _Executive Regulations Decree-Law No. 33.txt": {
        "law_name": "Cabinet Resolution - Executive Regulations of Federal Decree-Law No. 33",
        "version_year": 2022,
        "language": "en"
    },
    "Federal Decree by Law No. (33) of 2021 Concerning Regulating Labour Relations.txt": {
        "law_name": "Federal Decree-Law No. 33 of 2021 - Labour Relations",
        "version_year": 2021,
        "language": "en"
    },
    "Federal Decree by Law No. (47) of 2021 Concerning the Unified General Rules of Employment in the United Arab Emirates.txt": {
        "law_name": "Federal Decree-Law No. 47 of 2021 - Unified General Rules of Employment",
        "version_year": 2021,
        "language": "en"
    },
    "Federal Decree-Law No. 9 of 2022 Concerning Domestic Workers.txt": {
        "law_name": "Federal Decree-Law No. 9 of 2022 - Domestic Workers",
        "version_year": 2022,
        "language": "en"
    },
    "Federal Decree-Law No. 13 of 2022 Concerning Unemployment Insurance Scheme.txt": {
        "law_name": "Federal Decree-Law No. 13 of 2022 - Unemployment Insurance Scheme",
        "version_year": 2022,
        "language": "en"
    },
}

all_chunks = []

for filename, meta in FILE_METADATA.items():
    filepath = Path(TEXT_DIR) / filename
    
    if not filepath.exists():
        print(f" Skipping {filename} — file not found")
        continue
    
    print(f"Processing {filename}...")
    raw_text = filepath.read_text(encoding="utf-8")
    
    chunks = build_chunks(
        raw_text=raw_text,
        law_name=meta["law_name"],
        version_year=meta["version_year"],
        language=meta["language"],
        source_file=filename
    )
    
    all_chunks.extend(chunks)
    print(f"   {len(chunks)} chunks extracted")

# Save to JSON
os.makedirs(Path(OUTPUT_FILE).parent, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    # LawChunk is a dataclass, so convert to dict first
    json.dump([{"text": c.text, "metadata": c.metadata} for c in all_chunks], f, 
              ensure_ascii=False, indent=2)

print(f"Done. {len(all_chunks)} total chunks saved to {OUTPUT_FILE}")