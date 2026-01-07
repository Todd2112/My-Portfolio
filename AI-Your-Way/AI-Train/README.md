# AI-Train: Production-Grade Document Ingestion Pipeline

AI-Train is a local-first document processing system that ingests, classifies, and organizes knowledge from multiple sources without sending data to external APIs. Built on a triple-LLM architecture, it routes tasks intelligently across three specialized models to minimize compute waste while maintaining high accuracy.

**Core Principle:** Document ingestion should be fast, cheap, and private. AI-Train achieves this by running entirely on local infrastructure with zero recurring costs.

---

## What It Does

AI-Train transforms unstructured content into organized, queryable knowledge:

- **Extracts text** from PDFs, Word documents, HTML pages, and plain text files
- **Classifies content** into categories (Healthcare, Technology, Science, Finance, Literature, History, General)
- **Chunks intelligently** while preserving sentence boundaries and document structure
- **Analyzes links** to recommend related content based on user-defined goals
- **Stores persistently** in human-readable JSONL format with chunk relationship tracking
- **Crawls websites** with configurable depth and page limits

All processing happens locally. No data leaves your network. No API keys. No usage limits. No recurring costs.

---

## Why It Exists

Cloud-based document processing creates structural problems:

**The API Tax**  
Services like GPT-4 or Claude charge per token regardless of task complexity. Classifying a document into one of seven categories uses the same 175B parameter model as writing an essay. You pay for 100× more compute than necessary.

**The Context Reset**  
Every session starts from zero. Ingested knowledge disappears when the chat ends. You re-pay to re-ingest the same documents repeatedly.

**The Data Sovereignty Problem**  
Your proprietary content passes through vendor servers. You trust their privacy policies, accept their terms of service changes, and hope they don't get breached.

AI-Train eliminates all three:
- **Intelligent routing:** 70% of tasks handled by a 1B model (classification), 20% by a 3B model (summaries), 10% by an 8B model (reasoning)
- **Persistent storage:** All content stored locally in JSONL format, survives sessions indefinitely
- **Complete privacy:** Network disconnected after initial model download, zero telemetry

---

## Architecture

### Triple-LLM Intelligence Layer

AI-Train uses three specialized models instead of one generalized model:

| Brain | Model | Size | Role | Response Time | Temperature |
|:------|:------|-----:|:-----|:--------------|:------------|
| **Classifier** | llama3.2:1b-instruct-q4_K_M | 1B | Document categorization | 4–6s | 0.0 (deterministic) |
| **Parser** | llama3.2:3b-instruct-q8_0 | 3B | Summary generation, entity extraction | 8–12s | 0.1 (low creativity) |
| **Reasoner** | llama3:8b-instruct-q5_K_M | 8B | Link analysis, multi-hop reasoning | 10–15s | 0.1 (logical consistency) |

**Why Three Models?**

Using GPT-4 for every task wastes compute:
- Classifying "Is this about healthcare?" → Uses 175B parameters, needs ~1B
- Summarizing a document → Uses 175B parameters, needs ~3B
- Analyzing link relevance → Uses 175B parameters, needs ~8B

**Result:** 60–70% of requests routed to the 1B model, achieving 10–100× cost efficiency.

### System Prompts (Role Discipline)

Each brain has a locked system prompt to prevent hallucination:

**Classifier Brain:**
```
Strict document classifier.
Choose exactly ONE category from: Technology, Science, History, 
Literature, Finance, Healthcare, General.

Medical procedures, CPT, ICD, CMS → Healthcare
Academic research → Science
Software/hardware → Technology

Return ONLY the category name. No explanation.
```

**Parser Brain:**
```
Document auditor.
Describe ONLY what is explicitly present.
Do not infer purpose or intent.
Do not add outside knowledge.
```

**Reasoner Brain:**
```
Research assistant.
Refine existing answers and analyze relevance.
Do not add facts beyond the context.
Output valid JSON when requested.
```

### Processing Pipeline

```
Input (URL, File, or Manual Text)
    ↓
[File Type Detection]
    ├─ PDF → pdfplumber → OCR fallback → PyPDF2 fallback
    ├─ DOCX → python-docx (paragraph extraction)
    ├─ HTML → BeautifulSoup (sanitize scripts/nav/ads)
    └─ TXT → UTF-8 decode
    ↓
[Link Analysis - Reasoner Brain, 8B]
    • Identifies relevant links BEFORE content cleaning
    • Hybrid LLM + keyword scoring
    • Returns JSON recommendations
    ↓
[Text Normalization]
    • HTML tag removal
    • Whitespace normalization
    • ASCII fallback encoding
    ↓
[Classification - Classifier Brain, 1B]
    • Sample first 3000 chars
    • Remove numeric tables
    • Single category label
    ↓
[Smart Chunking]
    • 2048 chars per chunk
    • 256 char overlap for context
    • Preserve sentence boundaries
    • Filter by goal keywords (optional)
    ↓
[Persistence - Thread-Safe JSONL]
    • Unique doc_id and chunk_id
    • Relationship tracking (prev/next chunks)
    • Optional entity extraction (first chunk only)
    ↓
[Summary Generation - Parser Brain, 3B]
    • PDF-aware (describes document type)
    • Content-aware (summarizes topic)
    • 1-2 sentence summaries
```

---

## Key Features

### Multi-Format Document Processing

**PDF Extraction with Intelligent Fallback**
```
pdfplumber (text-based PDFs) 
    ↓ [garbled output detected]
OCR via Tesseract (scanned PDFs)
    ↓ [OCR unavailable or failed]
PyPDF2 (basic extraction)
```

Automatically handles:
- Text-based PDFs with tables
- Scanned/image-based PDFs
- Partially corrupted PDFs
- Encrypted PDFs (attempts recovery)

**Word Document Processing**
- Extracts paragraphs with proper separation
- Preserves document structure
- Handles complex formatting

**HTML Sanitization**
- Removes scripts, navigation, ads, forms
- Preserves semantic content
- Optimized for embedding generation

### Smart Content Chunking

- **2048 characters per chunk** with 256 character overlap
- **Sentence boundary preservation** (splits at periods, not mid-sentence)
- **Instructional content detection** (keeps "how to", "step-by-step", tutorials)
- **Question filtering** (removes standalone questions, keeps instructional ones)
- **Goal-based filtering** (optional keyword relevance scoring)

### Web Crawling

- **Breadth-first search (BFS)** traversal
- **Configurable depth** (0–5 levels) and page limits (1–100 pages)
- **Same-domain enforcement** with URL normalization
- **Automatic deduplication** via normalized URLs
- **Content validation** (spam detection, minimum length checks)

### Persistent Storage

**Append-Only JSONL Format**
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

**Why JSONL?**
- Human-readable (grep, jq, text editors work)
- Zero-dependency (pure Python I/O)
- Atomic writes (thread-safe with file locks)
- Trivial backup (copy file)
- Streaming reads (process line-by-line)

### Link Analysis & Recommendations

**Hybrid Reasoning Approach:**

1. **Primary:** Reasoner Brain (8B model)
   - Analyzes up to 15 candidate links
   - Multi-hop reasoning about relevance
   - Returns JSON-structured recommendations

2. **Fallback:** Keyword matching
   - Activates if LLM parsing fails
   - Scores links by goal keyword overlap
   - Threshold: 20/100 minimum score

**Example Output:**
```json
{
  "url": "https://example.com/related-page",
  "link_text": "Advanced Configuration Guide",
  "context_snippet": "This guide covers advanced setup...",
  "relevance_reason": "Contains detailed implementation steps for user's goal",
  "method": "llm",
  "confidence": "high",
  "action": "ingest_recommended"
}
```

---

## Performance Benchmarks

### Test Environment

**Hardware:**
- CPU: Intel Core i3-1115G4 (11th Gen, 3.0GHz, 2 cores/4 threads)
- RAM: 36GB DDR4
- GPU: Intel UHD Graphics (integrated, no dedicated GPU)
- Storage: NVMe SSD
- Cost: ~$700 (used laptop)

### Real-World Metrics (20 Sample Requests)

**Classifier Brain (1B Model):**

| Metric | Value |
|:-------|:------|
| Mean response | 7.76s |
| Median response | 5.76s |
| 95th percentile | 10.15s |
| Fastest | 3.92s |
| Slowest | 18.31s (cold start) |
| Excluding cold starts | 6.45s avg |

**Full Pipeline Performance:**
- Single document: 10–20 seconds (extract + classify + chunk + persist + summarize)
- Web crawl (20 pages): 3–5 minutes
- PDF with OCR: 30–60 seconds (varies by page count)

**Resource Usage:**
- Memory: <2GB RAM during processing
- CPU: 60–80% during inference, <5% idle
- Disk I/O: Sequential appends (minimal latency)
- Network: Zero API calls after model download

---

## Cost Analysis

### Traditional Approach (GPT-4 API)

100 requests/day × 30 days:
- Classification (30 req/day): 900 × $0.03 = $27.00
- Generation (50 req/day): 1,500 × $0.03 = $45.00
- Verification (20 req/day): 600 × $0.03 = $18.00

**Monthly: $90.00 | Annual: $1,080.00**

### AI-Train Approach (Local)

100 requests/day × 30 days:
- Classification: 1B model, local = $0.00
- Generation: 3B model, local = $0.00
- Verification: 8B model, local = $0.00

**Monthly: $0.00 | Annual: $0.00**

**Break-Even Analysis:**
- Hardware cost: $700 (one-time)
- Cloud API cost: $90/month
- Break-even: 7.8 months
- 2-year savings: $1,460

---

## Use Cases

### Medical Billing Knowledge Base

**Challenge:** Ingest CMS fee schedules, CPT code updates, ICD-10 crosswalks without exposing proprietary billing data to external APIs.

**How AI-Train Solves It:**
- Classifier detects clinical terminology (CPT, HCPCS, ICD) → assigns "Healthcare"
- Parser preserves tabular data (fee schedules, code mappings)
- Chunking respects code list boundaries (no mid-table splits)
- Link reasoner identifies related documents (CPT updates → fee schedule changes)

**Result:** Private, queryable medical billing knowledge base with zero vendor access.

### Technical Documentation Archive

**Challenge:** Crawl vendor docs, API references, changelogs while maintaining cross-references between versions.

**How AI-Train Solves It:**
- Classifier assigns "Technology" to software/hardware content
- Link reasoner follows "Related API" and "See Also" links
- Chunking preserves code examples intact
- Summary identifies document types (API reference, tutorial, migration guide)

**Result:** Searchable technical archive with preserved documentation relationships.

### Legal Research Repository

**Challenge:** Ingest case law, statutes, regulatory filings while maintaining citation networks.

**How AI-Train Solves It:**
- Chunking preserves citation structure
- Link reasoner identifies precedent chains (cases citing other cases)
- Entity extraction captures parties, dates, statutes (optional)
- Persistent storage maintains document relationships

**Result:** Private legal research database with complete citation tracking.

---

## Technical Specifications

### Models Used

```python
llm_classifier = LLMManager("llama3.2:1b-instruct-q4_K_M")
llm_parser = LLMManager("llama3.2:3b-instruct-q8_0")
llm_reasoner = LLMManager("llama3:8b-instruct-q5_K_M")
```

**Total Model Storage:** ~7GB (one-time download via Ollama)

### Configuration Parameters

```python
CHUNK_SIZE = 2048              # Characters per chunk
CHUNK_OVERLAP = 256            # Overlap for context preservation
MIN_TEXT_LENGTH = 200          # Minimum valid content length
KEYWORD_FALLBACK_THRESHOLD = 20  # Minimum keyword score for link relevance
EXTRACT_ENTITIES = False       # Optional entity extraction (env flag)
```

### Supported File Types

| Format | Handler | Features |
|:-------|:--------|:---------|
| PDF | pdfplumber → OCR → PyPDF2 | Table extraction, fallback chain |
| DOCX | python-docx | Paragraph extraction |
| HTML | BeautifulSoup | Tag sanitization |
| TXT | UTF-8 decode | Direct ingestion |

### API Endpoints

```
GET  /                      # Web interface
GET  /api/stats             # Ingestion statistics
POST /api/ingest            # Ingest URL or manual text
POST /api/ingest/file       # Upload and ingest file
POST /api/ingest/crawl      # Crawl website
POST /api/db/init           # Reset document store
POST /api/db/delete         # Delete document store
GET  /api/kb/entries        # Knowledge base stats
```

---

## Limitations & Design Choices

### What AI-Train Does NOT Do

**No Vector Search**  
AI-Train stores raw chunks, not embeddings. Retrieval requires separate RAG implementation.

**No Real-Time Updates**  
Document store is append-only. Updates require re-ingestion.

**No Multi-User Auth**  
Single-user design. Multi-tenancy requires authentication layer.

**No Distributed Processing**  
Single-threaded Flask. Horizontal scaling requires Gunicorn/NGINX.

### Why These Choices?

**Append-Only Storage:** Simplicity over complexity. No schema migrations, no transaction overhead, trivial backup/restore.

**No Vector DB:** Embeddings are domain-specific. AI-Train provides ingestion; you choose embedding strategy.

**Single-User Design:** Reduces complexity. Enterprise deployments add auth middleware as needed.

---

## Comparison to Alternatives

| Feature | AI-Train | GPT-4 API | Pinecone | LangChain |
|:--------|:---------|:----------|:---------|:----------|
| **Cost/month** | $0 | $90–200 | $70–200 | Varies |
| **Data sovereignty** | Complete | Zero | Zero | Partial |
| **Context persistence** | Infinite | 128k tokens | Vector-dependent | Varies |
| **Network dependency** | None* | Required | Required | Required |
| **Rate limits** | None | Yes | Yes | Yes |
| **Customization** | Full source | Prompt-only | Config-only | Framework-dependent |

*After initial model download

---

## Commercial Licensing

AI-Train is available for commercial deployment under proprietary licensing.

**Ideal For:**
- Healthcare organizations (HIPAA-compliant document ingestion)
- Law firms (privileged document processing)
- Financial institutions (regulatory filing archives)
- Research labs (academic paper repositories)
- Enterprises (internal knowledge base construction)

**Licensing Options:**
- Single-deployment license
- Multi-tenant enterprise license
- Custom integration services
- White-label deployment

**Contact:** [Your Contact Information]

---

## Technical Requirements

### Minimum Specifications

| Component | Requirement |
|:----------|:------------|
| CPU | Intel i3 (11th gen) or AMD Ryzen 3 |
| RAM | 16GB (32GB recommended) |
| Storage | 50GB free (SSD) |
| OS | Windows 10/11, Linux, macOS |
| Network | Internet for model download only |

### Dependencies

```
Python 3.8+
Ollama (local LLM runtime)
Flask
BeautifulSoup4
Requests
pdfplumber (optional, for PDF support)
pytesseract + pdf2image (optional, for OCR)
python-docx (optional, for Word support)
```

---

## Philosophy

AI-Train is built on three principles:

**1. Local-First**  
Data sovereignty is non-negotiable. If your content leaves your network, you've lost control.

**2. Cost-Aware**  
Intelligent task routing eliminates compute waste. Most classification tasks don't need 175B parameters.

**3. Human-Readable**  
JSONL storage means no vendor lock-in. You can read, modify, and migrate your data with basic text tools.

Cloud-based AI services optimize for vendor revenue, not customer value. AI-Train optimizes for the opposite: zero recurring costs, complete data ownership, and predictable performance on commodity hardware.

---

## Status

**Current Version:** Production-ready  
**Last Updated:** January 2025  
**Deployment:** Local/on-premises only  
**License:** Proprietary (commercial licensing available)

The code is not open-source, but the architecture and principles are documented here for evaluation purposes.
