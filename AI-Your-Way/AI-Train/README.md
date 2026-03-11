# ai-train.py — Production Document Ingestion Pipeline

A fully local document ingestion system that extracts, classifies, chunks, and stores knowledge
from PDFs, Word docs, HTML pages, and websites — using three specialized LLMs routed by task
complexity. No cloud APIs. No recurring costs. No data leaving your network.

**Core principle:** Most ingestion tasks don't need a 175B parameter model. Route by complexity,
pay nothing.

→ [Code Snippets](snippets/)

---

## The Problem It Solves

Cloud document processing has three structural failures:

| Problem | Cloud Behavior | This System |
|:--------|:--------------|:------------|
| API tax | Every task hits a 175B model regardless of complexity | 1B for classification, 3B for summaries, 8B for reasoning |
| Context reset | Knowledge disappears when session ends | Append-only JSONL survives indefinitely |
| Data sovereignty | Proprietary content passes through vendor servers | Network disconnected after model download |

---

## Architecture

### Triple-LLM Routing

| Brain | Model | Size | Temperature | Role |
|:------|:------|-----:|:-----------:|:-----|
| Classifier | llama3.2:1b-instruct-q4_K_M | 1B | 0.0 | Document categorization |
| Parser | llama3.2:3b-instruct-q8_0 | 3B | 0.1 | Summaries, entity extraction |
| Reasoner | llama3:8b-instruct-q5_K_M | 8B | 0.1 | Link analysis, multi-hop reasoning |

60–70% of requests routed to the 1B classifier. The 8B reasoner only activates for link
analysis — and only before text cleaning, so raw HTML link context is preserved.

→ [snippets/triple_llm_pipeline.py](snippets/triple_llm_pipeline.py)

### Processing Pipeline

```
Input (URL, File, or Manual Text)
    ↓
[File Type Detection]
    ├─ PDF → pdfplumber → garbled-text detection → OCR fallback → PyPDF2 fallback
    ├─ DOCX → python-docx
    ├─ HTML → BeautifulSoup sanitization
    └─ TXT → UTF-8 decode
    ↓
[Link Analysis — Reasoner Brain, 8B]
    Runs BEFORE text cleaning to preserve HTML link context
    Hybrid: LLM primary, keyword scoring fallback
    ↓
[Text Normalization]
    HTML tag removal, whitespace cleanup, ASCII fallback
    ↓
[Classification — Classifier Brain, 1B]
    First 3000 chars, numeric tables stripped, single label output
    ↓
[Smart Chunking]
    2048 chars, 256 overlap, sentence boundary preservation
    Optional goal-based keyword filtering
    ↓
[Persistence — Thread-Safe JSONL]
    Unique doc_id + chunk_id, prev/next relationship tracking
    Optional entity extraction (first chunk only)
    ↓
[Summary — Parser Brain, 3B]
    PDF-aware prompt, 1-2 sentence output
```

---

## Key Features

### PDF Extraction with Intelligent Fallback

Three extraction methods tried in order. Each result checked by a garbled-text detector
before acceptance — symbol ratio above 40% or repeated character patterns trigger fallback.

```
pdfplumber (table-aware, structured PDFs)
    ↓ [garbled-text detected: symbol ratio > 40% or repeated patterns]
pytesseract OCR (scanned/image-based PDFs)
    ↓ [OCR unavailable or failed]
PyPDF2 (basic text extraction)
    ↓ [all methods fail]
RuntimeError
```

→ [snippets/garbled_text_detection.py](snippets/garbled_text_detection.py)  
→ [snippets/pdf_fallback_chain.py](snippets/pdf_fallback_chain.py)

### Smart Chunking

- 2048 chars per chunk, 256 char overlap for context continuity
- Sentence boundary preservation — splits at periods, never mid-sentence
- Instructional content detection — keeps "how to", "step-by-step", tutorial content intact
- Standalone question filtering — removes noise questions, preserves instructional ones
- Goal-based filtering — optional keyword relevance pass before persistence

→ [snippets/goal_based_filtering.py](snippets/goal_based_filtering.py)

### Chunk Relationship Tracking

Every chunk stores `prev_chunk_id` and `next_chunk_id`. Retrieval systems can walk the
chain to reconstruct surrounding context when a single chunk isn't sufficient.

→ [snippets/chunk_persistence.py](snippets/chunk_persistence.py)

### Hybrid Link Analysis

8B reasoner analyzes up to 15 candidate links against the user's goal before text cleaning.
Keyword scoring activates automatically if LLM returns unparseable JSON.

→ [snippets/hybrid_link_analysis.py](snippets/hybrid_link_analysis.py)

### Web Crawler

- BFS traversal with configurable depth (0–5) and page limits (1–100)
- Same-domain enforcement, URL normalization, automatic deduplication
- Content validation before ingestion (spam detection, minimum length)
- One crawl-level summary generated after all pages ingested

---

## Performance Benchmarks

**Hardware:** Intel Core i3-1115G4 (11th Gen), 36GB RAM, integrated GPU — ~$700 used laptop.

**Classifier Brain (1B) — 20 sample requests:**

| Metric | Value |
|:-------|:------|
| Mean response | 7.76s |
| Median response | 5.76s |
| 95th percentile | 10.15s |
| Fastest | 3.92s |
| Slowest (cold start) | 18.31s |
| Excluding cold starts | 6.45s avg |

**Full pipeline (single document):** 10–20s  
**Web crawl (20 pages):** 3–5 minutes  
**PDF with OCR:** 30–60s  
**Memory usage:** <2GB RAM  
**Monthly cost:** $0

---

## Cost Comparison

100 requests/day, 30 days:

| Approach | Monthly | Annual |
|:---------|:-------:|:------:|
| GPT-4 API (single model) | $90.00 | $1,080.00 |
| This system (local, 3 models) | $0.00 | $0.00 |

Hardware break-even vs. cloud: **7.8 months**  
2-year net savings: **$1,460**

---

## Use Cases

**Medical Billing** — Ingest CMS fee schedules, CPT updates, ICD-10 crosswalks without
exposing proprietary billing data. Classifier detects clinical terminology, chunking
respects code list boundaries, link reasoner follows CPT update chains.

**Technical Documentation** — Crawl vendor docs and API references. Link reasoner follows
"Related API" and "See Also" links. Chunking preserves code examples intact.

**Legal Research** — Ingest case law and regulatory filings. Link reasoner identifies
precedent chains. Entity extraction captures parties, dates, statutes.

---

## JSONL Storage Format

```json
{
  "chunk_id": "doc_a3f92b1e4c5d_chunk_0",
  "doc_id": "doc_a3f92b1e4c5d",
  "source": "https://example.com/article",
  "category": "Technology",
  "text": "The document content...",
  "position": 0,
  "prev_chunk_id": null,
  "next_chunk_id": "doc_a3f92b1e4c5d_chunk_1",
  "token_estimate": 512,
  "entities": ["Python", "API", "REST"],
  "created_at": "2025-01-06T14:23:45"
}
```

Human-readable, zero-dependency, streamable, trivially backupable.

---

## API Endpoints

```
GET  /                    # Web interface
GET  /api/stats           # Ingestion statistics
POST /api/ingest          # Ingest URL or manual text
POST /api/ingest/file     # Upload and ingest file
POST /api/ingest/crawl    # Crawl website
POST /api/db/init         # Reset document store
POST /api/db/delete       # Delete document store
GET  /api/kb/entries      # Knowledge base stats
```

---

## Setup

### 1. Install Ollama and pull models
```bash
ollama pull llama3.2:1b-instruct-q4_K_M
ollama pull llama3.2:3b-instruct-q8_0
ollama pull llama3:8b-instruct-q5_K_M
```

### 2. Install dependencies
```bash
pip install flask requests beautifulsoup4 lxml pdfplumber PyPDF2 python-docx
# Optional OCR support:
pip install pytesseract pdf2image
# Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Configure vault path
Edit `VAULT_DIR` at the top of `ai-train.py` to your local output directory.

### 4. Run
```bash
python ai-train.py
# API available at http://localhost:8000
```

---

## Hardware Requirements

| Component | Minimum | Notes |
|:----------|:--------|:------|
| CPU | Intel i3 11th gen / Ryzen 3 | More cores = faster inference |
| RAM | 16GB | 32GB+ recommended |
| Storage | 50GB SSD | Models ~7GB, JSONL grows with usage |
| GPU | Not required | Integrated graphics sufficient |
| Network | Offline after model download | Zero runtime dependency |

---

## Security & Privacy

```
User Input → Flask (localhost:8000) → Ollama (localhost:11434) → JSONL (filesystem)
                                                                   ↑
                                                         Never leaves local network
```

- No telemetry, no analytics, no vendor access
- Works fully offline after initial model download
- System prompts lock each brain to its role — classifier cannot reason, reasoner cannot classify

---

## Comparison to Alternatives

| Feature | AI-Train | GPT-4 API | Pinecone | LangChain |
|:--------|:---------|:----------|:---------|:----------|
| Cost/month | $0 | $90–200 | $70–200 | Varies |
| Data sovereignty | Complete | Zero | Zero | Partial |
| Context persistence | Infinite | 128k tokens | Vector-dependent | Varies |
| Network dependency | None* | Required | Required | Required |
| Rate limits | None | Yes | Yes | Yes |

*After initial model download

---

## Status

**Last updated:** January 2025  
**Deployment:** Local / on-premises only  
**License:** Proprietary

The full script is not open-source. Snippets and architecture documentation are provided
for evaluation purposes. Commercial licensing available on request.
