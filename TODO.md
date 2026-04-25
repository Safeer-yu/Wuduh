# UAE Labor Law RAG Chatbot — Project Checklist

> **Stack:** PyMuPDF · LangChain · ChromaDB · OpenAI (text-embedding-3-small + GPT-4o) · Streamlit · Docker · Azure Container Apps

---

## Week 1 — Environment Setup & PDF Parsing

### Environment & Repo
- [x] Create GitHub repo with folder structure (`data/`, `src/`, `notebooks/`, `tests/`)
- [x] Set up Python virtual environment and `requirements.txt`
- [x] Create `.env` template and add it to `.gitignore`
- [x] Write a minimal `README.md` with project description and setup instructions

### PDF Acquisition
- [ ] Download Federal Decree-Law No. 33 of 2021 (Labour Law) from uaelegislation.gov.ae
- [ ] Download all amendments: 2022, 2023, and 2024 versions
- [ ] Download Arabic versions of the same laws
- [ ] Store PDFs in `data/raw/` with clear filenames (e.g. `labour_law_2021_en.pdf`)

### PDF Parsing
- [ ] Write PyMuPDF script to extract text from English PDFs and verify output quality
- [ ] Extract Arabic PDFs and verify Arabic text is not garbled (check Unicode, RTL)
- [ ] Detect and handle scanned pages — flag them or apply OCR fallback
- [ ] Save cleaned text to `data/processed/` as `.txt` or `.json` per document
- [ ] Sanity check: count articles extracted, spot-check 5 articles manually

---

## Week 2 — Chunking, Embeddings & Bilingual Retrieval

### Chunking Strategy
- [ ] Decide chunking unit: by Article vs fixed token size — document the decision
- [ ] Write chunker that splits by article number (e.g. "Article 1", "المادة 1")
- [ ] Add overlap strategy for long articles that exceed token limits

### Metadata Tagging
- [ ] Tag each chunk with: `article_number`, `law_name`, `year`, `language`, `is_amendment`
- [ ] Tag amendment chunks with `amends_article` reference for recency filtering
- [ ] Inspect metadata on 10 sample chunks to confirm correctness

### Embeddings & Vector Store
- [ ] Set up ChromaDB locally with a persistent storage directory
- [ ] Embed all chunks with `text-embedding-3-small` and load into ChromaDB
- [ ] Make the embedding script idempotent — re-running it should not duplicate data

### Bilingual Retrieval Testing
- [ ] Test English query → English chunk retrieval (e.g. "sick leave entitlement")
- [ ] Test Arabic query → Arabic chunk retrieval (e.g. "كم يوم إجازة مرضية")
- [ ] Test cross-lingual retrieval — Arabic query finds English chunks and vice versa
- [ ] Log retrieval results in a notebook and note any issues to fix in Week 3

---

## Week 3 — RAG Pipeline, Prompting & Amendment Handling

### Core RAG Pipeline
- [ ] Build LangChain retrieval chain: query → embed → retrieve → generate
- [ ] Write system prompt: cite article numbers, answer only from context, stay neutral
- [ ] Add conversation memory (`ConversationBufferMemory` or equivalent)
- [ ] Test multi-turn conversation: context carried across turns?

### Amendment Versioning
- [ ] Implement retrieval filter: prefer chunks with the highest `year` for the same article
- [ ] Test: ask about an amended article — confirm 2024 version is returned, not 2021
- [ ] Add instruction in prompt: "If multiple versions exist, use the most recent."

### Hallucination Fallback
- [ ] Add fallback when no relevant chunks found: return a clear "not found" message
- [ ] Set a similarity score threshold — reject low-confidence chunks from context
- [ ] Test with out-of-scope question (e.g. "What is UAE corporate tax?") — should not hallucinate

---

## Week 4 — Streamlit Chat UI

### UI Layout
- [ ] Build basic Streamlit chat interface with message history
- [ ] Add language toggle (English / Arabic) in the sidebar
- [ ] Apply RTL text direction when Arabic is selected (CSS injection)

### Source Transparency
- [ ] Display retrieved source chunks in a collapsible "Sources" expander below each answer
- [ ] Show article number, law name, and year for each source chunk

### Trust & Polish
- [ ] Add legal disclaimer: "This chatbot provides general information, not legal advice."
- [ ] Add a "Clear conversation" button to reset memory and chat history
- [ ] Manual end-to-end test: run 10 questions through the full UI

---

## Week 5 — Docker & Azure Deployment

### Docker
- [ ] Write `Dockerfile` (Python base image, copy code, expose port 8501)
- [ ] Write `docker-compose.yml` for local dev with env vars mounted
- [ ] Build and run image locally — confirm app works inside the container
- [ ] Push image to Azure Container Registry (ACR)

### Azure Deployment
- [ ] Create Azure Container Apps environment (portal or CLI)
- [ ] Deploy container from ACR to Azure Container Apps
- [ ] Store all API keys in Azure Key Vault — no hardcoded secrets

### ChromaDB Persistence
- [ ] Decision: persist ChromaDB to Azure Blob Storage OR migrate to Pinecone — document choice
- [ ] Implement chosen strategy and test vector store survives a container restart
- [ ] Test the deployed app end-to-end via the public URL

---

## Week 6 — Evaluation, Documentation & Portfolio

### Answer Quality Evaluation
- [ ] Write 30 evaluation questions (15 English, 15 Arabic): gratuity, sick leave, termination, hours…
- [ ] Write ground-truth answers by reading the actual law text
- [ ] Run all 30 questions through the chatbot and record answers + retrieved chunks
- [ ] Score each answer: correct article cited? factually correct? any hallucinations?
- [ ] Identify top 3 failure cases and document a fix for each

### Corpus Expansion
- [ ] Add at least one related law (e.g. DIFC Employment Law or Free Zone regulations)
- [ ] Re-embed and update the vector store with new documents

### Documentation & Portfolio
- [ ] Write final `README.md` with architecture diagram, setup instructions, and demo link
- [ ] Create architecture diagram: PDF → chunker → embedder → ChromaDB → LangChain → GPT-4o → Streamlit
- [ ] Record a 2–3 min screen demo showing the chatbot in both languages
- [ ] Update resume / LinkedIn with this project (RAG, Arabic NLP, Azure deployment)
- [ ] Make the GitHub repo public and share 🎉
