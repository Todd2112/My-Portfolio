# merge_vector.py — Vectorization & FAISS Index Service

Phase 2 of the AI-Train pipeline. Converts Phase 1 JSONL output into a
persistent, versioned, searchable vector knowledge base using a locked local
embedding model and FAISS. Exposes a Flask API for vectorization and search.

**Embeddings are infrastructure, not a black box. Every index is deterministic,
metadata-complete, and validated before it can be queried.**

→ [Code Snippets](snippets/)

---

## Position in the Pipeline

```
Phase 1 — ai-train.py
    Crawl → Clean → Classify → Chunk → Summarize → JSONL output

Phase 2 — merge_vector.py  ← this service
    Embed → Filter outliers → Build FAISS index → Persist versioned artifacts

Phase 3 — ask_ai.py
    Load index → Validate model/dim → Retrieve → Rerank → Synthesize
```

Phase 2 is the conversion layer. It takes unstructured text with metadata and
produces a binary FAISS index and a paired metadata blob that Phase 3 can load
and validate without any additional configuration.

---

## The Three Failures It Prevents

### Metadata Loss

Most pipelines embed text and discard provenance. Search results return text
fragments with no context about where they came from or what they contain.

Every document entering the FAISS index carries its full Phase 1 metadata through:
`doc_id`, `source`, `category`, `created_at`, `summary`, `total_tokens`.
Retrieval results include all of these fields — not just the text snippet.

→ [snippets/metadata_preservation.py](snippets/metadata_preservation.py)

### Non-Deterministic Indexing

Incremental or streaming outlier detection produces different indexes from the
same input depending on processing order. The index geometry is unstable.

All embeddings are computed first, then a stable mean/std is derived from the
complete set before any filtering. Same input → same index, every time.
The 3-sigma threshold (default 3.0) retains 99.7% of a normal distribution.

→ [snippets/deterministic_outlier_detection.py](snippets/deterministic_outlier_detection.py)

### Model Drift

Querying an index with a different embedding model or dimension than it was
built with produces silently wrong results — FAISS returns high scores for
semantically unrelated documents with no error.

The metadata blob records `embedding_model` and `embedding_dim` at build time.
The `/api/topk` endpoint validates both before executing any query. Mismatch
returns HTTP 409 with the expected and found values — fails loudly, not silently.

→ [snippets/query_time_validation.py](snippets/query_time_validation.py)

---

## Architecture

### Locked Embedding Model

```python
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"   # 768-dimensional
EMBEDDING_DIM        = 768
```

Single model, locked at config level. Not configurable per-request. Model is
loaded once on first use and cached for the process lifetime — the server is
immediately available before the model finishes warming.

→ [snippets/model_cache_singleton.py](snippets/model_cache_singleton.py)

### Vectorization Pipeline (`/api/vectorize`)

```
JSONL input (file upload or raw text)
    ↓
[parse_jsonl]
    Extract text + preserve all Phase 1 metadata fields
    Skip invalid JSON lines with warning (non-fatal)
    ↓
[build_faiss_index]
    Encode all texts → complete embeddings array
    Compute mean/std from full set (deterministic)
    Flag outliers: distance > (3σ × std_norm)
    Filter embeddings and documents in sync
    Build IndexFlatL2 (exact search)
    ↓
[persist_index_artifacts]
    Timestamped FAISS .bin file
    Paired .pkl metadata blob (embedding_model, embedding_dim, documents)
    ↓
Response: file paths + counts (total_chunks, outliers_removed)
```

### Search Pipeline (`/api/topk`)

```
Query string + file paths
    ↓
[Load FAISS + metadata blob]
    ↓
[Validate embedding_model and embedding_dim]
    Mismatch → HTTP 409 (conflict) with expected vs. found
    ↓
[Encode query with get_model()]
    ↓
[FAISS IndexFlatL2.search(query_emb, top_k)]
    ↓
[Build results with full metadata]
    text (truncated at 500 chars), doc_id, source, category,
    summary, total_tokens, created_at, distance
```

### Versioned Artifacts

Every vectorization run produces a timestamped pair:

```
Phase2_KBs/ai_train_core/
├── faiss_index_mpnet_20250115_143022.bin
├── meta_map_mpnet_20250115_143022.pkl
├── faiss_index_mpnet_20250116_091145.bin
└── meta_map_mpnet_20250116_091145.pkl
```

Rolling back to a prior index is a config change, not a rebuild.
`ask_ai.py`'s `/api/kb/browse` discovers all paired versions automatically.

→ [snippets/versioned_artifact_persistence.py](snippets/versioned_artifact_persistence.py)

---

## API Endpoints

### Vectorize

```
POST /api/vectorize
Content-Type: multipart/form-data

jsonl_file:        JSONL file upload (Phase 1 output)
jsonl_text:        Raw JSONL string (alternative to file upload)
outlier_thresh:    Float, default 3.0 (3-sigma threshold)
exclude_outliers:  Boolean string "true"/"false", default "true"
```

**Response:**
```json
{
  "status": "success",
  "embedding_model": "all-mpnet-base-v2",
  "total_chunks": 1847,
  "outliers_removed": 12,
  "faiss_index": "Phase2_KBs/ai_train_core/faiss_index_mpnet_20250115_143022.bin",
  "meta_map":    "Phase2_KBs/ai_train_core/meta_map_mpnet_20250115_143022.pkl"
}
```

### Search

```
POST /api/topk
Content-Type: application/json

{
  "query":       "What are the CPT codes for appendectomy?",
  "top_k":       5,
  "faiss_index": "Phase2_KBs/ai_train_core/faiss_index_mpnet_20250115_143022.bin",
  "meta_map":    "Phase2_KBs/ai_train_core/meta_map_mpnet_20250115_143022.pkl"
}
```

**Response:**
```json
{
  "status": "success",
  "query": "What are the CPT codes for appendectomy?",
  "embedding_model": "all-mpnet-base-v2",
  "results": [
    {
      "rank": 1,
      "distance": 0.18,
      "text": "CPT 44950 is the code for open appendectomy...",
      "doc_id": "doc_001",
      "source": "https://cms.gov/billing-codes",
      "category": "Healthcare",
      "summary": "Billing codes for appendectomy procedures",
      "total_tokens": 412,
      "created_at": "2025-01-15T10:22:31"
    }
  ]
}
```

**Model mismatch response (HTTP 409):**
```json
{
  "status": "error",
  "message": "Embedding model mismatch",
  "expected": "all-mpnet-base-v2",
  "found": "all-MiniLM-L6-v2"
}
```

---

## Performance Benchmarks

**Hardware:** Intel Core i3-1115G4 (11th Gen), 36GB RAM, integrated GPU.

| Operation | Duration | Notes |
|:----------|:---------|:------|
| Model load (first call) | 2–8s | Cached after first call |
| Encode 1,000 documents | 45–90s | CPU-only, 768-dim |
| Outlier detection | <1s | NumPy vectorized |
| FAISS index build | <1s | IndexFlatL2, 1k vectors |
| FAISS search (top-5) | <5ms | Exact search |
| Artifact persistence | <1s | Binary pickle + FAISS write |
| **Total (1k docs)** | **~60–100s** | One-time cost per JSONL batch |

Monthly compute cost: $0.

---

## Setup

### 1. Install dependencies
```bash
pip install flask faiss-cpu sentence-transformers numpy
```

### 2. Download the embedding model (one time)
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-mpnet-base-v2")
model.save("C:/Models/pdf_teacher/all-mpnet-base-v2")
```

### 3. Configure paths
Edit `LOCAL_MODEL_DIR` and `VAULT_DIR` at the top of `merge_vector.py`.

### 4. Run
```bash
python merge_vector.py
# API available at http://localhost:9000
```

### 5. Vectorize a Phase 1 JSONL file
```bash
curl -X POST http://localhost:9000/api/vectorize \
  -F "jsonl_file=@output.jsonl" \
  -F "outlier_thresh=3.0"
```

---

## Hardware Requirements

| Component | Minimum | Notes |
|:----------|:--------|:------|
| CPU | Intel i3 11th gen / Ryzen 3 | More cores = faster batch encoding |
| RAM | 8GB | 768-dim × 50k vectors ≈ 150MB |
| Storage | 5GB SSD | Model weights + index files |
| GPU | Not required | CPU encoding is sufficient |

---

## Design Decisions

**FAISS IndexFlatL2 (exact search)**  
Approximate indexes (IVF, HNSW) are faster for >100k vectors but require
training and introduce recall trade-offs. For the target scale (<100k vectors),
exact search is both fast enough and 100% recall.

**Single locked model**  
`ask_ai.py` supports multi-model KBs. `merge_vector.py` produces KBs for the
core AI-Train pipeline, which uses one model. Locking the model at config level
eliminates an entire class of dimension-mismatch bugs.

**Timestamped artifacts, not overwrite**  
Each vectorization run is preserved. Debugging a retrieval regression means
loading the prior index — no rebuild required.

**Dict-based model cache over module-level variable**  
Module-level variables can be shadowed in test environments. A dict is
explicit, inspectable in debug sessions, and extendable if a second model
is ever added.

---

## Status

**Last updated:** January 2025  
**Deployment:** Local / on-premises only  
**License:** Proprietary

The full script is not open-source. Snippets and architecture documentation
are provided for evaluation purposes.
