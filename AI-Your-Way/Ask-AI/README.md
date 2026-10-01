# Ask-AI: Hybrid Retrieval & Document Intelligence System

**100% Local • CPU-Bound Engine • Multi-Format Document Processing • Web Search Fallback**

Local FAISS Vectors • Sub-Document Ingestion • Deterministic Grounding • Zero Cloud Dependencies

![Ask-AI Telemetry & Retrieval Trace](https://raw.githubusercontent.com/Todd2112/My-Portfolio/master/AI-Your-Way/Ask-AI/ask_ai_llm_monitor_cli.png)
*Figure 1: Real-time execution diagnostic pipeline. Left: System telemetry, prefill/generation token latency, and hybrid retrieval traces. Right: Local Ollama server executing a two-pass multi-document extraction on commodity CPU hardware.*

> **Commercial Architecture Showcase**  
> Ask-AI is a proprietary, single-tenant commercial software package. This repository serves as an architectural benchmark and technical showcase containing sanitized core logic snippets. Source code access and enterprise licensing are available upon request. See [Availability & Licensing](#availability--licensing).

---

## The Problem

Standard, off-the-shelf RAG implementations often suffer from structural document truncation, context drift across conversation turns, uncontrolled monthly cloud API costs, and silent model hallucinations.

| Challenge | Standard RAG Approach | Ask-AI Approach |
|:---|:---|:---|
| **Large Document Ingestion** | Fixed chunking ignoring document structure | **3-Tier Sub-Doc Ingestion:** Numbered/unnumbered ToCs & line gap-ratio clustering |
| **Retrieval Accuracy** | Single-vector cosine similarity search | **Hybrid RRF Search:** 768d FAISS vectors + Lexical IDF + Active Doc Session Boost |
| **Multi-Turn Context** | Global re-queries on every turn | **Sticky Context Locking:** Detects referential phrasing ("summarize this") to lock target doc |
| **Context Window Overhead** | Arbitrary top-$k$ chunk dumping | **Dynamic Anchoring:** Head/Mid/Tail structural slices + top-40% semantic windowing |
| **Hallucination Control** | Unvalidated generation output | **Deterministic Grounding:** Dual-check token overlap & vector similarity gate (<40% fallback) |
| **System Observability** | Black-box API calls | **Decoupled Telemetry Sidecar:** Real-time RAM, heap, loop lag, and t/s tracking on port 8002 |
| **Data Privacy & Cost** | External cloud LLM dependency ($/token) | **100% Local CPU Execution:** $0 recurring API overhead, zero external data leakage |

---

## Architecture Overview

```text
[ Document / URL ] ──► (1) Ingestion & Sub-Doc Processor ──► JSONL / SQLite / FAISS
                                                                  │
[ Query Input ] ────► (7) FastAPI Route (/api/query)              │
                               │                                  ▼
                               ├──────────────────────► (2) Hybrid Retrieval Engine
                               │                         • FAISS + IDF + Title Boost
                               │                         • Active Doc Session Boost (2.5x)
                               │                         • Reciprocal Rank Fusion (RRF)
                               │                                  │
                               ├──────► (3) Session Manager ◄─────┤
                               │         • Sticky Doc Locking     │
                               │         • Multi-Doc Extraction   │
                               │                                  ▼
                               ├──────────────────────► (4) Dynamic Windowing & Hotspots
                               │         • Anchor Slices (B/M/E)  │
                               │         • Top-Score Allocator    │
                               │                                  │
                               │                                  ▼
                               ├──────────────────────► (5) Synthesis & Grounding
                               │         • Ollama Streaming       │
                               │         • Overlap/Vector Check   │
                               │         • Auto-Ingest Web DDGS   │
                               │
                               └──────────────────────► (6) Telemetry Sidecar (127.0.0.1:8002)
```

---

## Core Engineering Capabilities & Code Architecture

### 1. Structure-Aware Ingestion & Segmentation

Extracts raw text across multi-file formats (PDF with `pytesseract` OCR fallback, DOCX, TXT, MD, URL web scraping), detects structural boundaries using multi-tier ToCs and gap-ratio clustering, and registers documents with domain classifications and keyword tags.

```python

def split_into_subdocuments(text: str, toc_entries: list[dict] = None) -> list[dict]:
    """Splits full document text into structural sub-documents using ToCs or gap ratios."""
    # Tier 1 & 2: Match Numbered or Unnumbered ToC entries
    if toc_entries:
        sub_docs = []
        for i, entry in enumerate(toc_entries):
            title = entry["title"]
            start_pos = text.find(title)
            end_pos = text.find(toc_entries[i + 1]["title"]) if i + 1 < len(toc_entries) else len(text)
            if start_pos != -1:
                sub_docs.append({"title": title, "content": text[start_pos:end_pos]})
        if sub_docs:
            return sub_docs

    # Tier 3: Gap-Ratio Clustering based on heading spacing
    lines = text.split("\n")
    heading_indices = [i for i, line in enumerate(lines) if re.match(r"^(SECTION|CHAPTER|\d+\.\d+)", line, re.I)]
    
    if len(heading_indices) > 1:
        gaps = np.diff(heading_indices)
        median_gap = np.median(gaps)
        chunks, current_chunk = [], []
        
        for idx, line in enumerate(lines):
            if idx in heading_indices and current_chunk and len(current_chunk) > median_gap * 0.5:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
            current_chunk.append(line)
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        return [{"title": f"SubDoc_{i+1}", "content": c} for i, c in enumerate(chunks)]

    return [{"title": "Full Document", "content": text}]
```

---

### 2. Hybrid Retrieval Engine (`query_kb`)

Queries a 768-dimensional L2-normalized FAISS vector index (`nomic-embed-text`), computes sparse lexical IDF scores with a **2.5x Active Document Session Boost**, and fuses ranks using Reciprocal Rank Fusion:

$$RRF_{score}(d) = \frac{1}{60 + r_{vec}} + \frac{1}{60 + r_{lex}}$$

```python

def query_kb(query_vec: np.ndarray, query_terms: list[str], active_doc_id: str, k: int = 20) -> list[dict]:
    # 1. FAISS Dense Retrieval
    distances, indices = faiss_index.search(query_vec.astype(np.float32), k)
    vec_results = {idx: rank + 1 for rank, idx in enumerate(indices[0]) if idx != -1}

    # 2. Lexical IDF + Session Continuity Boosting
    lex_scores = {}
    for doc_id, doc in kb_registry.items():
        tf_idf = sum(doc["idf_tags"].get(term, 0) for term in query_terms)
        
        # Apply Title Exact Match & Session Continuity Boost (2.5x)
        if doc_id == active_doc_id:
            tf_idf *= 2.5
        if any(term in doc["title"].lower() for term in query_terms):
            tf_idf *= 1.5
            
        lex_scores[doc_id] = tf_idf

    # Rank lexical candidates
    sorted_lex = sorted(lex_scores.items(), key=lambda x: x[1], reverse=True)[:k]
    lex_results = {doc_id: rank + 1 for rank, (doc_id, _) in enumerate(sorted_lex)}

    # 3. Reciprocal Rank Fusion (RRF)
    all_keys = set(vec_results.keys()) | set(lex_results.keys())
    rrf_scores = []
    for key in all_keys:
        r_vec = vec_results.get(key, 1000)
        r_lex = lex_results.get(key, 1000)
        score = (1.0 / (60 + r_vec)) + (1.0 / (60 + r_lex))
        rrf_scores.append((key, score))

    rrf_scores.sort(key=lambda x: x[1], reverse=True)
    return [kb_registry[key] for key, _ in rrf_scores[:k]]
```

---

### 3. Session Memory & Context Stickiness

Manages persistent conversation states in SQLite (`data/sessions.db`) alongside an in-memory deque. Intercepts referential follow-ups (*"summarize this"*, *"tell me more"*) to lock retrieval directly to the active document.

```python

STICKY_TRIGGERS = {"this", "it", "that", "more", "summarize", "explain further", "continue"}

def resolve_sticky_doc_id(query: str, session_history: deque, last_doc_id: str) -> str:
    """Detects implicit follow-up queries and locks context to the active document."""
    words = set(query.lower().split())
    
    # Check if query consists primarily of referential triggers or short follow-ups
    if words.intersection(STICKY_TRIGGERS) and (len(words) <= 6 or last_doc_id):
        return last_doc_id
    return None

def save_turn(db_path: str, session_id: str, role: str, content: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO session_turns (session_id, role, content, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (session_id, role, content)
        )
```

---

### 4. Dynamic Context Windowing & Hotspots

Prevents narrative omission during summarization by pairing structural Head, Middle, and Tail 1,200-character anchor slices with paragraph semantic windows scoring within 40% of the top vector match.

```python
def select_semantic_windows(paragraphs: list[dict], top_score: float, score_threshold_ratio: float = 0.40) -> str:
    """Filters and aggregates narrative windows within 40% of top vector score."""
    cutoff = top_score * score_threshold_ratio
    selected = [p for p in paragraphs if p["score"] >= cutoff]
    
    # Extract structural head, middle, and tail anchors (1200 chars each)
    full_text = "\n\n".join([p["text"] for p in paragraphs])
    head_anchor = full_text[:1200]
    mid_idx = len(full_text) // 2
    mid_anchor = full_text[mid_idx - 600 : mid_idx + 600]
    tail_anchor = full_text[-1200:]
    
    semantic_body = "\n\n".join([p["text"] for p in selected])
    return f"--- ANCHORS ---\n{head_anchor}\n...\n{mid_anchor}\n...\n{tail_anchor}\n\n--- SEMANTIC WINDOWS ---\n{semantic_body}"
```

---

### 5. Synthesis, Grounding & Web Fallback

Streams local model synthesis via Ollama. Evaluates generation fidelity against source context using token precision and vector similarity, triggering an asynchronous DuckDuckGo web search and auto-ingestion if confidence drops below 40%.

```python

def validate_synthesis(generated_text: str, source_context: str) -> bool:
    """Deterministic grounding check; returns False if overlap drops below 40%."""
    gen_words = set(re.findall(r"\w+", generated_text.lower()))
    ctx_words = set(re.findall(r"\w+", source_context.lower()))
    
    if not gen_words:
        return False
        
    overlap = len(gen_words.intersection(ctx_words)) / len(gen_words)
    return overlap >= 0.40

async def query_web_fallback(query: str) -> str:
    """Executes DDG search and extracts top web content on low confidence."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            async with httpx.AsyncClient() as client:
                res = await client.get(r["href"], timeout=5.0)
                if res.status_code == 200:
                    results.append(res.text[:1500])
    return "\n\n".join(results)
```

---

### 6. Telemetry & Monitoring Sidecar

Decoupled performance tracking framework using the `@Telemetry.gate` decorator. Monitors sync/async execution timing, RSS memory (`psutil`), heap allocation (`tracemalloc`), and loop lag via an independent HTTP sidecar daemon running on port 8002.

```python

class Telemetry:
    DATA = {"metrics": {}, "last_retrieval": {}}

    @classmethod
    def gate(cls, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            res = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            
            name = func.__name__
            cls.DATA["metrics"][name] = cls.DATA["metrics"].get(name, []) + [elapsed]
            cls.DATA["rss_memory_mb"] = psutil.Process().memory_info().rss / (1024 * 1024)
            return res
        return wrapper

# Sidecar Metrics Server
sidecar_app = FastAPI()

@sidecar_app.get("/metrics")
def get_metrics():
    return Telemetry.DATA
```

---

### 7. FastAPI Service Routes & Streaming

Core API interface serving UI assets, routing direct metadata queries to knowledge registries, processing RAG retrieval pipelines, and streaming NDJSON token feeds to client interfaces.

```python

app = FastAPI()

@app.post("/api/query")
@Telemetry.gate
async def api_query(request: Request):
    body = await request.json()
    user_query = body.get("query")
    session_id = body.get("session_id")

    async def generate_stream():
        # Check feedback queue / direct metadata routing
        if is_metadata_query(user_query):
            yield json.dumps({"type": "metadata", "data": lookup_registry(user_query)}) + "\n"
            return

        # Execute Retrieval & Context Selection
        context = retrieve_and_build_context(user_query, session_id)
        
        # Stream model response chunks
        async for chunk in stream_ollama_synthesis(user_query, context):
            yield json.dumps({"type": "token", "content": chunk}) + "\n"

    return StreamingResponse(generate_stream(), media_type="application/x-ndjson")
```

---

## Hardware Benchmarks (Commodity CPU)

Evaluated on consumer laptop hardware (**Intel Core i3 11th Gen, 36 GB RAM, Integrated CPU Graphics**), running resident local ~3B parameter Ollama models (~3.1 GB memory footprint).

| Workload Scenario | Execution Path | Avg. Duration | Pipeline Operations |
|:---|:---|:---:|:---|
| **Single-Document Retrieval & Summary** | Full-Text Injection Path | ~150 s | Anchor extraction + single LLM synthesis pass |
| **Two-Document Comparative Analysis** | Multi-Doc Extraction Pipeline | ~138 s | Two extraction passes + cross-synthesis pass |
| **Vector Similarity Search (FAISS)** | Hybrid `query_kb` Path | ~2.2 s | 768d vector dot product + RRF ranking |
| **System Resource Allocation** | Memory / CPU Footprint | ~3.1 GB | Stable resident footprint across continuous operations |

> *Note: Local CPU execution prioritizes total data privacy and $0 operating overhead over raw token speed. Wall times scale down significantly when deployed on hardware with dedicated GPU acceleration.*

---

## Technical Stack

* **Service Framework:** Python 3.11+, FastAPI, Uvicorn, AsyncIO
* **Vector Indexing & Retrieval:** FAISS (`faiss-cpu`), `nomic-embed-text` (768d), Custom Lexical IDF Engine
* **Inference Engine:** Ollama (`sovereign-kb` task-specific Modelfiles)
* **Storage & Persistence:** SQLite (`data/sessions.db`), `JSONL` Document Registries
* **System Telemetry:** `psutil`, `tracemalloc`, Independent HTTP Sidecar Daemon (`port 8002`)

---

## Contract Engineering & Enterprise Services

I am available for contract engagements and specialized technical consulting around private AI deployment:

* **Private & Offline RAG Architecture:** Custom local knowledge base deployment and context pipeline design.
* **Complex Document Ingestion:** Building OCR pipelines, structural ToC extractors, and domain-specific chunkers.
* **Inference & Memory Optimization:** CPU/GPU resource profiling, quantization selection, and latency reduction.
* **Deterministic Verification:** Implementing answer validation gates, factual overlap scoring, and hallucination guardrails.

---

## Availability & Licensing

Ask-AI is distributed as a single-tenant, closed-source commercial software package. 

For commercial licensing, custom integration inquiries, or system demos:

* **Contact:** realtodd@yahoo.com
* **GitHub:** [Todd2112](https://github.com/Todd2112)
* **LinkedIn:** [Todd Lipscomb](https://www.linkedin.com/in/todd-lipscomb-670458290/)

---

*© TML Investments LLC. All rights reserved. Proprietary software.*
