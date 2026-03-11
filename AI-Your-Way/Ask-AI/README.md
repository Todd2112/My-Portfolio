# ask_ai.py — Multi-KB RAG System with Cross-Model Retrieval

A fully local RAG system that queries multiple knowledge bases simultaneously,
reranks results using each KB's own embedding model, validates LLM augmentation
semantically before accepting it, and scores answer confidence using five
weighted signals.

**No single-model lock-in. No hallucinations accepted silently. No cloud APIs.**

→ [Code Snippets](snippets/)

---

## The Problem It Solves

Standard RAG systems have three structural failures:

| Problem | Standard RAG | This System |
|:--------|:------------|:------------|
| Single-model trap | One embedding model per deployment | Each KB declares its own model in metadata |
| Reranking gap | FAISS cosine similarity alone causes topic mismatch | Per-model semantic reranker corrects ranking |
| Hallucination on augmentation | LLM refines answers but adds invented facts | Keyword overlap + embedding similarity gate rejects drift |

---

## Architecture

### 8-Stage Query Pipeline

```
User Query
    ↓
[Stage 1 — Multi-KB Retrieval]
    Each KB queried with its own embedding model via FAISS
    Results annotated with source_kb and kb_model
    ↓
[Stage 2 — Per-Model Reranking]
    Results grouped by embedding model
    Each group reranked by its own LocalReranker instance
    Prevents cross-model score contamination
    ↓
[Stage 3 — Cross-KB Score Fusion]
    All groups merged, sorted by rerank score descending
    Scores comparable across models (normalized cosine [0,1])
    ↓
[Stage 4 — Answer Extraction]
    Best-scoring entry selected
    Wiki artifacts, footnotes, formatting noise removed
    ↓
[Stage 5 — LLM Augmentation + Validation Gate]
    Reasoning agent (8B) refines for clarity
    Rejected if keyword overlap < 30% OR embedding similarity < 70%
    Original KB answer preserved on rejection
    ↓
[Stage 6 — Confidence Scoring]
    5 weighted signals: outcome type, user feedback,
    RAG consensus, rerank score, statistical baseline
    ↓
[Stage 7 — Web Fallback]
    DuckDuckGo activates only if KB produced no answer
    5-second timeout, sentence-boundary truncation
    ↓
[Stage 8 — Structured Response]
    Answer + all scoring signals + source metadata
```

→ [snippets/query_pipeline.py](snippets/query_pipeline.py)

### Triple-LLM Agent System

| Agent | Model | Size | Temperature | Role |
|:------|:------|-----:|:-----------:|:-----|
| Initializer | llama3.2:1b-instruct-q4_K_M | 1B | 0.0 | Query classification |
| Orchestrator | llama3.2:3b-instruct-q8_0 | 3B | 0.3 | Task routing |
| Reasoner | llama3:8b-instruct-q5_K_M | 8B | 0.3 | Answer augmentation |

---

## Key Features

### Metadata-Driven KB Loading

KBs are self-describing — the embedding model and dimension live in the metadata
file, not in config or environment variables. Dimension mismatch is caught at
load time, not silently at query time.

```
metadata declares:  embedding_model = "BioBERT-embeddings"
                    embedding_dim   = 768

loader validates:   FAISS index dimension == 768  ✓
                    model output dimension == 768  ✓
                    document count == vector count ✓
```

Any mismatch raises `RuntimeError` immediately.

→ [snippets/metadata_driven_kb_loading.py](snippets/metadata_driven_kb_loading.py)

### Per-Model Semantic Reranking

FAISS cosine similarity is insufficient for semantic relevance. A document about
"Python snakes" and "Python exception handling" can have near-identical FAISS
scores because "Python" appears frequently in both.

The `LocalReranker` uses sentence embeddings to compute true semantic similarity.
One reranker instance per embedding model — shared across KBs that use the same
model to avoid redundant memory loading. Batch encoding (32 texts per batch)
gives 3-5× speedup over sequential.

→ [snippets/local_reranker.py](snippets/local_reranker.py)

### Augmentation Validation Gate

LLMs improve answer clarity but also hallucinate. Two independent checks before
accepting any augmented answer:

- **Keyword overlap ≥ 30%** — prevents topic drift
- **Embedding similarity ≥ 70%** — prevents semantic divergence

If either check fails, the original KB answer is returned unchanged.

→ [snippets/augmentation_validation.py](snippets/augmentation_validation.py)

### RAG Consensus Scoring

Measures agreement between the final answer and all retrieved snippets using
the 60th percentile similarity score.

- Mean: one weak snippet tanks the score
- Median: ignores high-quality snippets
- **60th percentile: tolerates weak matches while rewarding strong consensus**

→ [snippets/rag_consensus_scoring.py](snippets/rag_consensus_scoring.py)

### Confidence Scoring

Five weighted signals combined into one score:

| Signal | Weight | Value Range |
|:-------|:------:|:------------|
| Outcome type | 0.35 | KB_DIRECT=1.0, KB_AUGMENTED=0.9, WEB=0.4, FAIL=-1.0 |
| User feedback | 0.25 | approve=1.0, edit=0.0, reject=-1.0 |
| RAG consensus | 0.25 | 60th percentile similarity |
| Rerank score | 0.10 | Top result semantic similarity |
| Statistical baseline | 0.05 | Always 0.5 |

All signals normalized from [-1, 1] → [0, 1] before weighting so negative
signals (FAIL, reject) drag the score down without special-case logic.

→ [snippets/confidence_scoring.py](snippets/confidence_scoring.py)

### Web Fallback

DuckDuckGo search activates only when KB retrieval produces no answer.
5-second timeout via `ThreadPoolExecutor`. Snippet truncated at sentence
boundary (not mid-word). Labeled `WEB` in source_type so callers know
the answer came from outside the KB.

---

## Performance Benchmarks

**Hardware:** Intel Core i3-1115G4 (11th Gen), 36GB RAM, integrated GPU.

**Loaded:** 3 knowledge bases (~50,000 vectors total, <3GB RAM)

| Operation | Duration |
|:----------|:---------|
| FAISS retrieval (3 KBs) | 20–40ms |
| Reranking (15 pairs, batched) | 50–80ms |
| Cross-KB score fusion | <5ms |
| Answer extraction + cleaning | <10ms |
| LLM augmentation (8B) | 8–12s |
| Web fallback | 2–5s |
| **Total without augmentation** | **~100ms** |
| **Total with augmentation** | **~10s** |

**Resource usage:**
- FAISS indexes: ~1.5GB
- Embedding models: ~1GB (3 models cached)
- Session memory: <50MB
- Monthly cost: $0

---

## Cost Comparison

| Approach | Monthly | Annual |
|:---------|:-------:|:------:|
| Pinecone + GPT-4 | $160–400 | $1,920–4,800 |
| This system (local) | $0 | $0 |

---

## API Endpoints

```
GET  /api/health              # System health + loaded KB count
GET  /api/kb/list             # Available KB directories
GET  /api/kb/browse/<kb>      # Versioned FAISS/metadata file pairs
POST /api/kb/load_multiple    # Load KB using metadata as source of truth
GET  /api/kb/list_loaded      # Currently loaded KBs with metadata
POST /api/kb/unload           # Remove KB from memory
POST /api/query               # Main query endpoint
POST /api/feedback            # Log answer feedback (approve/edit/reject)
```

**Example query response:**
```json
{
  "status": "success",
  "answer": "CPT 44950 is used for open appendectomy procedures...",
  "source_type": "KB_AUGMENTED",
  "source_kb": "medical_kb|v2",
  "confidence": 0.85,
  "rerank_score": 0.92,
  "rag_score": 0.78,
  "augmented": true
}
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
pip install flask faiss-cpu sentence-transformers numpy
pip install duckduckgo-search  # optional web fallback
```

### 3. Configure paths
Edit `KB_ROOT` and `MODELS_ROOT` at the top of `ask_ai.py`.

### 4. Run
```bash
python ask_ai.py
# API available at http://localhost:8001
```

### 5. Load a KB
```bash
curl -X POST http://localhost:8001/api/kb/load_multiple \
  -H "Content-Type: application/json" \
  -d '{"kb_name": "my_kb", "pairs": [{"faiss_file": "faiss_index_v1.bin", "meta_file": "meta_map_v1.pkl", "version": 1}]}'
```

---

## Hardware Requirements

| Component | Minimum | Notes |
|:----------|:--------|:------|
| CPU | Intel i3 11th gen / Ryzen 3 | More cores = faster batch encoding |
| RAM | 16GB | 32GB+ recommended for multiple KBs |
| Storage | 20GB SSD | Varies with KB size |
| GPU | Not required | Integrated graphics sufficient |
| Network | Offline after model download | Zero runtime dependency |

---

## Comparison to Alternatives

| Feature | This System | Pinecone | Weaviate | LangChain |
|:--------|:-----------:|:--------:|:--------:|:---------:|
| Cost/month | $0 | $70–200 | $25–100 | Varies |
| Multi-model KB support | ✓ | ✗ | Limited | ✗ |
| Cross-KB retrieval | ✓ | Manual | Manual | ✗ |
| Local reranking | ✓ | ✗ | ✗ | External API |
| Augmentation validation | ✓ | ✗ | ✗ | ✗ |
| Confidence scoring | ✓ | ✗ | ✗ | ✗ |
| Data sovereignty | Complete | Zero | Zero | Partial |

---

## Security & Privacy

```
User Query → Flask (localhost:8001) → FAISS (local files) → Ollama (localhost:11434)
                                                              ↑
                                                    Never leaves local network
```

Web fallback is the only external call — opt-in, timeout-guarded, labeled in response.

---

## Status

**Last updated:** January 2025  
**Deployment:** Local / on-premises only  
**License:** Proprietary

The full script is not open-source. Snippets and architecture documentation are
provided for evaluation purposes. Commercial licensing available on request.
