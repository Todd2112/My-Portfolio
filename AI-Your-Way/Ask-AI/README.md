# Ask-AI: Hybrid Retrieval & Document Intelligence System

**100% Local • CPU-Bound Engine • Multi-Format Document Processing • Optional Web Search Fallback**

Local FAISS Vectors • Sub-Document Ingestion • Deterministic Grounding • No Cloud AI Dependencies

![Ask-AI Top Panel & Interface](https://raw.githubusercontent.com/Todd2112/My-Portfolio/master/AI-Your-Way/Ask-AI/ask_ai_top.png)
*Figure 1: Ask-AI system dashboard and primary query interface.*

> **Commercial Architecture Showcase**
> Ask-AI is a proprietary, single-tenant commercial software package. This repository is an architectural and technical showcase. Code snippets are simplified illustrations of the approach, not the shipped source. Licensing inquiries are welcome. See [Availability & Licensing](#availability--licensing).

---

## The Problem

Standard, off-the-shelf RAG implementations often suffer from structural document truncation, context drift across conversation turns, uncontrolled monthly cloud API costs, and silent model hallucinations.

| Challenge | Standard RAG Approach | Ask-AI Approach |
|:---|:---|:---|
| **Large Document Ingestion** | Fixed chunking ignoring document structure | **3-Tier Sub-Doc Ingestion:** Numbered/unnumbered ToCs & line gap-ratio clustering |
| **Retrieval Accuracy** | Single-vector cosine similarity search | **Hybrid RRF Search:** 768d FAISS vectors + Lexical IDF + Title Boost + Active Doc Session Boost |
| **Multi-Turn Context** | Global re-queries on every turn | **Sticky Context Locking:** Detects follow-ups that add no new content words ("tell me more about this") and locks the target doc |
| **Context Window Overhead** | Arbitrary top-$k$ chunk dumping | **Dynamic Anchoring:** Head/Mid/Tail structural slices + top-40% semantic windowing |
| **Hallucination Control** | Unvalidated generation output | **Validation Gate:** Keyword overlap and embedding similarity checked against retrieved text before an augmented answer is accepted |
| **System Observability** | Black-box API calls | **Decoupled Telemetry Sidecar:** Real-time RAM, heap, loop lag, and t/s tracking on port 8002 |
| **Data Privacy & Cost** | External cloud LLM dependency ($/token) | **Local CPU Execution:** $0 recurring API overhead. Documents never leave the machine; optional, labeled web search sends only the query |

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
                               │         • Optional Web Fallback  │
                               │                                  │
                               └──────────────────────► (6) Telemetry Sidecar (127.0.0.1:8002)
```

![Ask-AI Mid-Pipeline Trace](https://raw.githubusercontent.com/Todd2112/My-Portfolio/master/AI-Your-Way/Ask-AI/ask_ai_mid.png)
*Figure 2: Intermediate execution state, session tracking, and pipeline routing.*

---

## Core Engineering Capabilities & Code Architecture

> The snippets below are **simplified illustrations of the approach**, not the shipped source.

### 1. Structure-Aware Ingestion & Segmentation

Extracts raw text across multi-file formats (PDF with `pytesseract` OCR fallback, DOCX, TXT, MD, URL web scraping) and detects structural boundaries using multi-tier ToCs and gap-ratio clustering. ToC parsing is layout-agnostic: it handles one-line entries (`4  Basic Programming ..... 37`) as well as extractors that split number, title, and page onto separate lines, and it locates each real heading in the body even when titles wrap across lines. Very short sections are merged into their neighbors instead of being dropped.

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

Queries a 768-dimensional L2-normalized FAISS vector index (`nomic-embed-text`), computes sparse lexical IDF scores per chunk, applies a **3x title-match boost** and a **2.5x Active Document Session Boost**, and fuses the two rankings using Reciprocal Rank Fusion:

$$RRF_{score}(d) = \frac{1}{60 + r_{vec}} + \frac{1}{60 + r_{lex}}$$

```python
def query_kb(query: str, query_vec: np.ndarray, query_terms: set, active_doc_id: str, k: int = 40) -> list[dict]:
    # 1. FAISS dense retrieval
    distances, indices = faiss_index.search(query_vec.astype(np.float32), k)
    candidates = [load_chunk(int(i)) for i in indices[0] if i != -1]

    # 2. Per-chunk lexical IDF score and boosts
    for chunk, sim in zip(candidates, distances[0]):
        chunk["vector_score"] = float(sim)
        chunk["lexical_score"] = sum(term_idf(t) for t in query_terms & chunk["keywords"])

        boost = 1.0
        if chunk["doc_title"].lower() in query.lower():
            boost *= 3.0   # explicit title match
        if chunk["doc_id"] == active_doc_id:
            boost *= 2.5   # session continuity
        chunk["boost"] = boost

    # 3. Rank each signal independently, then fuse ranks (not raw scores)
    by_vec = {id(c): r for r, c in enumerate(sorted(candidates, key=lambda c: c["vector_score"], reverse=True))}
    by_lex = {id(c): r for r, c in enumerate(sorted(candidates, key=lambda c: c["lexical_score"], reverse=True))}

    for c in candidates:
        rrf = 1.0 / (60 + by_vec[id(c)] + 1) + 1.0 / (60 + by_lex[id(c)] + 1)
        c["score"] = rrf * c["boost"]

    return sorted(candidates, key=lambda c: c["score"], reverse=True)
```

---

### 3. Session Memory & Context Stickiness

Manages persistent conversation states in SQLite (`data/sessions.db`) alongside an in-memory deque. Follow-ups that add no new content words (*"tell me more about this"*) lock retrieval to the active document. A query that names a new subject (*"summarize Visual Studio"*) is treated as a topic change and routed normally.

```python
REFERENTIAL = {"this", "it", "that", "more", "tell", "about", "explain", "continue", "summarize"}

def resolve_sticky_doc_id(query: str, history: list) -> str | None:
    """Stick to the prior document only if the query adds no new content words."""
    if not history:
        return None
    remainder = extract_keywords(query) - REFERENTIAL
    return history[-1]["doc_id"] if not remainder else None

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

### 5. Synthesis, Grounding & Optional Web Fallback

Streams local model synthesis via Ollama. An augmented answer is accepted only if it passes both a keyword-overlap check and an embedding-similarity check against the retrieved text. Web search is an optional, clearly labeled fallback for when the knowledge base cannot answer; only the query is sent, and documents never leave the machine.

```python
def validate_synthesis(generated: str, source_context: str) -> bool:
    """Dual-check gate: keyword overlap AND embedding similarity must both pass."""
    kw_overlap = keyword_overlap(source_context, generated)
    emb_sim = cosine(embed(generated), embed(source_context))
    return kw_overlap >= 0.40 and emb_sim >= 0.65

async def query_web_fallback(query: str) -> str:
    """Optional: runs only when local retrieval produces no answer."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            async with httpx.AsyncClient() as client:
                res = await client.get(r["href"], timeout=5.0)
                if res.status_code == 200:
                    results.append(res.text[:1500])
    return "\n\n".join(results)
```

![Ask-AI Grounded Response Output](https://raw.githubusercontent.com/Todd2112/My-Portfolio/master/AI-Your-Way/Ask-AI/ask_ai_answer.png)
*Figure 3: Grounded response output with real-time scoring and source attribution.*

![Ask-AI Human-in-the-Loop Feedback Interface](https://raw.githubusercontent.com/Todd2112/My-Portfolio/master/AI-Your-Way/Ask-AI/ask_ai_bottom.png)
*Figure 4: Human-in-the-Loop (HITL) feedback module providing real-time answer verification, optional inline text editing, and Approve / Edit / Reject workflow control.*

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

![Ask-AI Telemetry & Retrieval Trace](https://raw.githubusercontent.com/Todd2112/My-Portfolio/master/AI-Your-Way/Ask-AI/ask_ai_llm_monitor_cli.png)
*Figure 5: Sidecar telemetry panel monitoring RAM, loop latency, prefill/generation rates, and local LLM execution.*

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
| **Single-Document Retrieval & Summary** | Full-Text Injection Path | ~150 s | Full-section injection + single LLM synthesis pass |
| **Two-Document Comparative Analysis** | Multi-Doc Extraction Pipeline | ~138 s | Two extraction passes + cross-synthesis pass |
| **Query Embedding** | `nomic-embed-text` on CPU | ~2.2 s | 768d embedding of the user query (FAISS search itself takes milliseconds) |
| **System Resource Allocation** | Memory / CPU Footprint | ~3.1 GB | Stable resident footprint across continuous operations |

> *Note: Local CPU execution prioritizes total data privacy and $0 operating overhead over raw token speed. Timings are observations from one cold-start test configuration, not guarantees. Wall times scale down significantly on hardware with dedicated GPU acceleration.*

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
