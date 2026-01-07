# Autonomous AI Agent Portfolio - Sales & Operations Agent Proposal

I have built autonomous AI agents with RAG.

**GitHub Portfolio:** https://github.com/Todd2112/My-Portfolio/tree/master/AI-Your-Way

---

## Portfolio & Proof of Work

Three production systems demonstrating autonomous decision-making, RAG pipelines, tool orchestration, and human-in-the-loop escalation.

---

## System 1: AI-Train - Production Ingestion Pipeline

**Repository:** https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/AI-Train/README.md

**What I Built:** Multi-source knowledge ingestion system with triple-LLM architecture

**Autonomy:**
- Classifies documents autonomously (1B model for speed)
- Generates summaries (3B model for accuracy)
- Analyzes link relevance with 8B reasoning model + keyword fallback
- Hybrid decision logic: LLM primary, deterministic fallback for robustness

**RAG Implementation:**
- Intelligent PDF extraction (pdfplumber → OCR → PyPDF2 fallback chain)
- Semantic chunking (2048 chars, 256 overlap) with goal-based filtering
- Vector-ready JSONL output for FAISS ingestion
- AST-aware chunking preserves code structure

**Tools:** BeautifulSoup, Tesseract OCR, Requests with retry logic

**Scale:** Handles PDFs, DOCX, TXT, HTML. BFS crawler (configurable depth/pages). Processes 100+ page documents.

**Risk Mitigation:** Copyright compliance (15-word quote limit), spam detection, content validation
```python
def extract_pdf_with_fallback(file_bytes: bytes) -> str:
    if pdfplumber:
        text = extract_pdf_with_structure(file_bytes)
        if not is_extraction_garbled(text):
            return text
    if OCR_AVAILABLE:
        return extract_pdf_with_ocr(file_bytes)
    if PyPDF2:
        return extract_pdf_basic(file_bytes)
```

---

## System 2: Ask AI - Multi-KB RAG Backend

**Repository:** https://github.com/Todd2112/My-Portfolio/tree/master/AI-Your-Way/Ask-AI

**What I Built:** Cross-knowledge-base retrieval system with semantic reranking and LLM augmentation

**Autonomy:**
- Routes queries across multiple vector stores automatically
- Semantic outlier filtering (0.7 similarity threshold)
- LLM augmentation with dual validation (keyword + embedding)
- Web search fallback via DuckDuckGo when confidence low
- Decision engine: Query → Multi-KB Retrieval → Rerank → Augment → Web Fallback

**RAG Implementation:**
- Vector search: FAISS indices with cosine similarity
- Per-model reranking: LocalReranker using SentenceTransformers
- Metadata-driven: Embedding model stored in KB metadata (single source of truth)
- Consensus scoring: 60th percentile similarity across retrieved chunks
- Confidence system: Weighted signals (outcome 35%, user 25%, RAG 25%, rerank 10%, stat 5%)

**Memory:** Session management (50 entries, 1-hour TTL), feedback queue, user signal tracking (approve/edit/reject)

**Scale:** Multi-KB support with cross-model compatibility. 5-10 retrieval calls for complex queries. Handles 768D and 384D embeddings simultaneously.

**Human Escalation:** Confidence thresholds trigger web fallback. "I couldn't find an answer" when all sources fail.
```python
def process_query_pipeline(query, active_kbs, rag_engines, rerankers):
    # Stage 1: Multi-KB retrieval
    for kb in active_kbs:
        results = rag_engines[kb].topk_retrieve(query)
    
    # Stage 2: Per-model reranking
    for model, results in group_by_model(all_results):
        reranked = rerankers[model].predict(query, results)
    
    # Stage 3: Cross-KB score fusion
    combined = sort_by_weighted_score(reranked)
    
    # Stage 4: LLM augmentation (if confident)
    if best_score >= AUGMENTATION_MIN_RERANK:
        augmented = augment_with_llm(answer, context)
        if validate_semantic_overlap(answer, augmented):
            return augmented
    
    # Stage 5: Web fallback (if needed)
    if not answer or confidence < threshold:
        return web_search(query)
```

---

## System 3: MyCoder - Self-Learning Coding Assistant

**Repository:** https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/My_Coder.md

**What I Built:** Agentic coding system with constitutional governance and CAG (Code-Aware Generation) memory

**Autonomy:**
- Feature manager: Auto-decomposes projects into testable features (A001, A002, etc.)
- Intent detection: Routes queries to appropriate agent (modify-target, review, fix, explain)
- CAG pipeline: Retrieves learned patterns → Modifies code → Verifies with reasoning LLM
- Hallucination detection: 5-layer validation with confidence scoring (0.0-1.0)
- Decision flow: Intent → Target Validation → RAG Retrieval → CAG Patterns → LLM Execution → Verification → Persistence (if safe)

**RAG Implementation:**
- AST-aware chunking: One function/class = one chunk (preserves semantic boundaries)
- Importance weighting: Scores chunks by docstring presence, length, reference count
- Symbol table: Deterministic retrieval for targeted edits (ClassName.method_name)
- Vector storage: NumPy-based FAISS with 768D embeddings

**Tools:** PowerShell validation (indentation, style checks), Python AST auditing (syntax, imports, function preservation), constitutional governance

**Memory:** RAG (persistent vector index), CAG (pattern-based learning), session state (conversation history with accepted/rejected flags)

**Human Escalation:** Code flagged as "unsafe to persist" (confidence < 0.6) requires manual review. Hallucination warnings with specific issues listed.

**Scale:** 2048-char semantic chunks with 512 overlap. Keeps last 100 learned patterns. Metrics logging (prompt/response tokens, duration).
```python
def detect_hallucinations(generated_code: str, original_code: str = "") -> Dict:
    report = {"hallucination_detected": False, "confidence": 1.0, "issues": []}
    
    try:
        ast.parse(generated_code)
    except SyntaxError:
        report["safe_to_persist"] = False
        return report
    
    # Layer 2: Placeholder detection (TODO, FIXME, ...)
    # Layer 3: Empty implementations (only "pass")
    # Layer 4: Function preservation (missing functions)
    # Layer 5: Import consistency
    
    report["safe_to_persist"] = report["confidence"] >= 0.6
    return report
```

---

## Requirements Mapping

| Your Requirement | My Implementation | GitHub Proof |
|------------------|-------------------|--------------|
| Autonomous Decision-Making | MyCoder CAG Pipeline: retrieve → reason → modify → verify. Ask AI: multi-KB routing → rerank → augment → web fallback | [MyCoder](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/My_Coder.md), [Ask-AI](https://github.com/Todd2112/My-Portfolio/tree/master/AI-Your-Way/Ask-AI) |
| RAG-Grounded Responses | FAISS + reranking + augmentation validation. AST-aware chunking with importance weighting. Semantic outlier filtering (0.7 threshold) | [Ask-AI](https://github.com/Todd2112/My-Portfolio/tree/master/AI-Your-Way/Ask-AI), [MyCoder](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/My_Coder.md) |
| Tool Usage | PDF extraction fallback chain. PowerShell validation, AST auditing. Web search, BFS crawler | [AI-Train](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/AI-Train/README.md) |
| Cross-Session Memory | Session management + feedback queue. Persistent RAG index + CAG pattern memory. Feature state tracking | [Ask-AI](https://github.com/Todd2112/My-Portfolio/tree/master/AI-Your-Way/Ask-AI), [MyCoder](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/My_Coder.md) |
| Confidence & Fallback Logic | Weighted confidence (outcome 35%, RAG 25%, rerank 10%). Hallucination detection (0-1.0 scores). Hybrid LLM + keyword fallback | [Ask-AI](https://github.com/Todd2112/My-Portfolio/tree/master/AI-Your-Way/Ask-AI), [MyCoder](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/My_Coder.md) |
| Human Escalation | "Unsafe to persist" flags when confidence < 0.6. Web fallback when RAG confidence low. Validation reports with actionable issues | [MyCoder](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/My_Coder.md), [Ask-AI](https://github.com/Todd2112/My-Portfolio/tree/master/AI-Your-Way/Ask-AI) |

---

## Technical Architecture

### RAG Pipeline (Ask AI)

1. Chunking: AST-aware (functions/classes as chunks) with importance weighting (0.0-1.0)
2. Embedding: SentenceTransformers with model validation (dimension checks)
3. Retrieval: FAISS (cosine similarity) + semantic outlier filtering (0.7 threshold)
4. Reranking: Per-model LocalReranker with batched encoding (32 batch size)
5. Augmentation: LLM refinement with dual validation (keyword overlap ≥30%, semantic similarity ≥70%)
6. Consensus: 60th percentile similarity across retrieved chunks (avoids outlier dominance)

- Model-Agnostic: Current implementation uses Ollama (local), trivially adaptable to OpenAI/Claude/Gemini APIs


### Agent Decision Logic (MyCoder)
```python
intent, target = detect_intent(user_input)  # Organizer LLM (1B)

if intent == "modify-target" and target:
    rag_results = rag.query(user_input, k=3)           # Vector search
    learned = cag_memory.get_relevant(user_input, k=2) # Pattern match
    revised_code = llm.generate("coding", prompt_with_context)  # 7B model
    verification = llm.generate("reasoning", verify_prompt)  # 3B model
    
    hallucination_report = detect_hallucinations(revised_code)
    if hallucination_report["safe_to_persist"]:
        persist_to_memory()
    else:
        flag_for_human_review()
```

### Ingestion Pipeline (AI-Train)
```python
text = extract_with_fallback(file_bytes)
category = llm_classifier.classify(text)  # 1B model (fast)
chunks = chunk_text(text, goal)           # Semantic + goal filtering
summary = llm_parser.summarize(chunks)    # 3B model (accurate)
links = llm_reasoner.analyze_links(html)  # 8B model (reasoning)

if llm_reasoning_fails:
    links = keyword_based_fallback(html, goal)
```

---

## Adaptation to Sales & Operations Agent

**Phase 1: RAG Foundation (Week 1-2)**
- Index SOPs, FAQs, pricing, policies using AI-Train pipeline
- Build multi-KB RAG backend (Ask AI architecture)
- Integrate CRM data as separate knowledge base

**Phase 2: Agent Logic (Week 3-4)**
- Adapt intent detection (lead qualification, meeting booking, follow-up)
- Implement confidence scoring for escalation
- Build tool integrations (CRM API, calendar, email/WhatsApp)

**Phase 3: Memory & Learning (Week 5-6)**
- Cross-session memory (conversation history)
- Feedback loop (successful/failed interactions)
- Pattern learning (CAG-style) for edge cases

**Key Differentiators:**
- Not rule-based: Uses RAG + LLM reasoning, not hardcoded if/else
- Confidence-aware: Escalates when uncertain (like Ask AI's web fallback)
- Tool orchestration: Multi-step workflows (retrieve → reason → act → verify)
- Error handling: Fallback chains (like AI-Train's PDF extraction)

---

## Screening Questions

**1. Describe your recent experience with similar projects**

Built in past 6 months (all on GitHub):
- AI-Train: Triple-LLM ingestion pipeline with hybrid decision logic
- Ask AI: Multi-KB RAG backend with semantic reranking, LLM augmentation, confidence scoring
- MyCoder: Self-learning coding assistant with CAG memory and constitutional governance

All use production-grade RAG (FAISS/NumPy), LLM orchestration (Ollama), and tool integration (PowerShell, AST, web search, PDF extraction).

Relevance:
- Ask AI's confidence system maps directly to your escalation requirement
- AI-Train's hybrid reasoning (LLM + fallback) ensures robustness in production
- MyCoder's hallucination detection prevents wrong/unsafe actions

**2. What techniques would you use to clean a data set?**

For Knowledge Ingestion (AI-Train):
- HTML Sanitization: BeautifulSoup to strip script/nav/footer/style tags
- Spam Detection: Keyword blacklist + 200-char minimum
- Deduplication: URL normalization for crawlers
- Encoding Normalization: UTF-8 with ASCII fallback
- Chunk Validation: Symbol ratio check (max 40% non-alphanumeric), repeated character patterns

For RAG Indexing (Ask AI):
- AST-aware chunking: Preserve function/class boundaries
- Outlier filtering: Remove retrieval results below 0.7 cosine similarity
- Metadata cleaning: Strip footnotes, wiki artifacts, normalize whitespace

For CRM/Conversation Data:
- PII redaction: Regex for emails, phones, SSNs
- Timestamp normalization: ISO 8601
- Empty field handling: Distinguish between null, "", and missing keys
- Duplicate detection: Fuzzy matching (Levenshtein distance)
```python
def sanitize_text(raw_text: str) -> str:
    soup = BeautifulSoup(raw_text, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

---

**GitHub Portfolio:** https://github.com/Todd2112/My-Portfolio/tree/master/AI-Your-Way

Looking forward to building a production autonomous agent together.
