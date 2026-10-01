# Ask-AI: Hybrid Retrieval & Document Intelligence System

**100% Local • CPU-Bound Engine • Multi-Format Document Processing • Web Search Fallback**

Local Vectors • Sub-Document Ingestion • Deterministic Grounding Checks • Zero Cloud Exposure

![Ask-AI Telemetry & Retrieval Trace](https://raw.githubusercontent.com/Todd2112/My-Portfolio/master/AI-Your-Way/Ask-AI/ask_ai_llm_monitor_cli.png)
*Figure 1: Real-time execution diagnostic pipeline. Left: System telemetry, prefill/generation token latency, and hybrid retrieval traces. Right: Local Ollama server executing a two-pass multi-document extraction on commodity CPU hardware.*

> **Commercial Architecture Showcase**  
> Ask-AI is a proprietary, single-tenant commercial software package. This repository serves as an architectural benchmark and technical showcase containing sanitized core logic snippets. Source code access and enterprise licensing are available upon request. See [Availability & Licensing](#availability--licensing).

---

## The Problem

Standard, off-the-shelf RAG implementations often suffer from structural document truncation, context drift across conversation turns, uncontrolled monthly cloud API costs, and silent model hallucinations.

| Challenge | Standard RAG Approach | Ask-AI (Sovereign Engine) Approach |
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
---

## The Problem
### 1. Structure-Aware Ingestion & Segmentation

Extracts raw text across multi-file formats (PDF with `pytesseract` OCR fallback, DOCX, TXT, MD, URL web scraping), detects structural boundaries using multi-tier ToCs and gap-ratio clustering, and registers documents with domain classifications and keyword tags.

```python
import re
import fitz  # PyMuPDF
import numpy as np

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
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        return [{"title": f"SubDoc_{i+1}", "content": c} for i, c in enumerate(chunks)]

    return [{"title": "Full Document", "content": text}]
