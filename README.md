<div align="center">
  
# My AI Engineering Portfolio

**Building production-grade local AI systems that eliminate recurring API costs**

[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Available%20for%20Licensing-green.svg)]()

[Featured Work](#featured-projects) • [Philosophy](#technical-philosophy) • [Contact](#connect)

</div>

---

## About

I design and deploy **local-first AI systems** that run entirely on your infrastructure—no cloud dependencies, no recurring API costs, no vendor lock-in.

My work focuses on three core capabilities:
- **Document Intelligence:** Multi-format ingestion with intelligent extraction
- **Knowledge Retrieval:** Multi-KB RAG with cross-model semantic search
- **Persistent Memory:** Stateful AI that maintains context across unlimited sessions

**Core Value Proposition:** What costs $90–200/month in cloud APIs runs locally for $0/month with better data sovereignty and predictable performance.

---

## Featured Projects

### 🚀 AI-Your-Way: Local AI Systems with Persistent Memory
**Production-grade coding assistant with infinite context and zero API costs**

A three-tier local AI architecture that eliminates the context amnesia problem. Uses specialized models (1B/3B/7B) routed by task complexity, with persistent memory stored locally in human-readable JSONL format.

**Key Metrics:**
- Classification: 4–6s response time (1B model)
- Code generation: 10–20s (7B model)
- Hardware: Consumer laptop (Intel i3, 36GB RAM, integrated GPU)
- Monthly cost: **$0** (vs $90–200 for cloud alternatives)

**Technical Highlights:**
- Triple-LLM architecture with role-specific system prompts
- RAG + CAG hybrid memory (semantic + pattern learning)
- Multi-layer validation pipeline (AST, style, hallucination detection)
- Break-even: 7.8 months vs cloud APIs

**[View Full Documentation →](AI-Your-Way/)**

---

### 📚 AI-Train: Document Ingestion Pipeline
**Multi-format document processing with intelligent extraction and classification**

A production-grade ingestion system that processes PDFs, Word docs, HTML, and text files with automatic fallback chains and web crawling capabilities.

**Key Features:**
- PDF extraction: pdfplumber → OCR → PyPDF2 fallback
- Triple-LLM classification (1B), summarization (3B), and link analysis (8B)
- Smart chunking with goal-based filtering
- BFS web crawling with same-domain enforcement

**Technical Highlights:**
- Garbled text detection with automatic OCR fallback
- Thread-safe JSONL persistence with chunk relationship tracking
- Hybrid reasoning: LLM primary, keyword fallback
- Healthcare-aware classification (CPT, ICD, HCPCS detection)

**[View Full Documentation →](AI-Train/)**

---

### 🔍 Ask-AI: Multi-KB RAG System
**Cross-model knowledge base retrieval with semantic validation**

A multi-knowledge-base RAG system that queries KBs built with different embedding models (BioBERT, MiniLM, MPNet) simultaneously, with per-model reranking and LLM augmentation.

**Key Features:**
- Multi-KB cross-model retrieval (query 3+ KBs with different embeddings)
- Per-model semantic reranking (local sentence transformers)
- Cross-KB score fusion with confidence scoring
- Answer augmentation with semantic validation (70% similarity threshold)

**Technical Highlights:**
- Metadata-driven model loading (single source of truth)
- RAG consensus scoring (60th percentile similarity)
- Web fallback with DuckDuckGo (5s timeout)
- Query performance: 100–150ms (KB only), 8–12s (with augmentation)

**[View Full Documentation →](Ask-AI/)**

---

## Architecture Philosophy

### Why Local-First?

Cloud-based AI services create three structural problems:

**The API Tax**  
You pay for 100× more compute than necessary. Classifying a document uses the same 175B model as writing an essay.

**The Context Reset**  
Knowledge disappears when sessions end. You re-pay to re-ingest the same documents repeatedly.

**The Data Sovereignty Problem**  
Your proprietary content passes through vendor servers. You trust their terms, accept their changes, hope they don't get breached.

### The Local Alternative

My systems eliminate all three:

| Challenge | Cloud Solution | Local Solution |
|:----------|:---------------|:---------------|
| **Compute Waste** | Single 175B model | 3-tier routing (1B/3B/8B) |
| **Context Loss** | 128k–200k token limits | Infinite (disk-based storage) |
| **Data Risk** | Vendor servers | Never leaves your network |
| **Cost** | $90–200/month | $0/month (after hardware) |

**Break-even: 7.8 months**

---

## Technical Philosophy

**1. Task-Appropriate Scaling**  
Route simple tasks (classification) to small models (1B), complex reasoning to larger models (8B). Don't use a 175B model to answer "Is this about healthcare?"

**2. Persistent Memory**  
Store context permanently in human-readable formats (JSONL). No vendor lock-in, no schema migrations, trivial backup.

**3. Semantic Validation**  
LLM augmentation is powerful but dangerous. Validate outputs with keyword overlap (30%) and embedding similarity (70%) thresholds.

**4. Model-Agnostic Architecture**  
Support multiple embedding models simultaneously. Medical KB uses BioBERT, legal KB uses LegalBERT—query both at once.

---

## Cost Analysis

### 2-Year Total Cost of Ownership

**Cloud API Approach (GPT-4):**
- Monthly: $90 (100 requests/day, mixed workload)
- Annual: $1,080
- 2-Year: **$2,160**

**Local Approach:**
- Hardware: $700 (one-time, consumer laptop)
- Monthly: $0
- Annual: $0
- 2-Year: **$700**

**Net Savings: $1,460 over 2 years**

**Additional Benefits:**
- No rate limits
- No network dependency
- No vendor ToS changes
- Complete data sovereignty

---

## Other Projects

Brief explorations and proofs-of-concept demonstrating specific techniques:

- **Web Keyword Crawler:** HTML parsing with trend detection
- **Reasoning AI Chatbot:** Explainable decision-making with intermediate vectors
- **Visual Data Pipeline:** Identity-preserving image generation with LoRA
- **PDF Teacher RAG:** Document Q&A with offline embeddings
- **Business Solutions Suite:** Content generation, SEO, social media automation

**[View Archive →](Other-Projects/)**

---

## Commercial Availability

These systems are available for **licensing and custom deployment**.

**Ideal For:**
- Healthcare organizations (HIPAA-compliant document processing)
- Law firms (privileged document search and analysis)
- Financial institutions (regulatory compliance knowledge bases)
- Enterprises (internal AI assistants with data sovereignty)
- Research labs (academic paper retrieval and analysis)

**Licensing Options:**
- Single-deployment license
- Multi-tenant enterprise license
- Custom integration services
- White-label deployment

---

## Technology Stack

**Core Technologies:**
- Python 3.8+, Flask, Ollama (local LLM runtime)
- FAISS (vector search), sentence-transformers (embeddings + reranking)
- NumPy, PyTorch (optional, for custom models)

**Optional Components:**
- pdfplumber, pytesseract (PDF extraction + OCR)
- python-docx (Word document parsing)
- BeautifulSoup4 (HTML cleaning)
- duckduckgo-search (web fallback)

**Hardware Requirements:**
- Minimum: Intel i3 (11th gen), 16GB RAM, 50GB storage
- Recommended: Intel i5+, 32GB RAM, NVMe SSD
- Optional: Dedicated GPU for faster inference

---

## Connect

**For commercial licensing inquiries:**  
📧 [your-email@example.com]  
💼 [LinkedIn Profile]  
🌐 [Personal Website]  
📂 GitHub: [Todd2112](https://github.com/Todd2112)

---

**Production-Ready • Zero API Costs • Complete Data Sovereignty**

