# Sovereign AI — Legal Discovery Engine
## User & Feature Guide — v3

| | |
|---|---|
| **Product** | Sovereign AI Legal Discovery Engine |
| **Version** | legal_proto_ver3.py |
| **Architecture** | FastAPI + Ollama (Local/CPU Only) |
| **Target Users** | Law firms, legal researchers, in-house counsel |

---

## 1. Product Overview

The Sovereign AI Legal Discovery Engine is a fully local, privacy-first document analysis platform. It ingests legal documents (PDF, DOCX, TXT), extracts structured findings using fine-tuned local LLM agents, and stores them in a multi-layer retrieval architecture that supports fast, precise legal queries — all without sending a single byte to a cloud provider.

> **KEY DIFFERENTIATOR:** All processing runs on-premises. No OpenAI. No Azure. No data ever leaves the machine. Fully compliant with attorney-client privilege and bar confidentiality rules.

### Core Capabilities

- Ingest PDF, DOCX, and TXT legal documents
- Automatic party identification (plaintiff, defendant, appellant, appellee)
- Structured finding extraction: holdings, precedents, dicta, dissents, admissions, contradictions
- Three-tier query engine: exact match → semantic search → LLM synthesis
- Case audit trail with full chronological chunk history
- Live dashboard: query stats, finding distributions, FAISS index health
- Prompt editor: create and modify extraction protocols without restarting

### System Requirements

| | |
|---|---|
| **OS** | Windows, Linux, or macOS |
| **Python** | 3.10+ |
| **RAM** | 16 GB minimum (32+ GB recommended for large documents) |
| **GPU** | Not required — CPU-only inference |
| **Ollama** | Running locally with `sovereign-auditor` and `sovereign-narrator` models loaded |
| **Port (API)** | 8001 |
| **Port (Telemetry)** | 8002 (internal only, not exposed to clients) |

---

## 2. Getting Started

### 2.1 Launch

```bash
python legal_proto_ver3.py
```

Then open: `http://localhost:8001`

Startup sequence (logged to console):
- SQLite Sovereign Ledger initialized
- FAISS Layer 2 bootstrapped from existing findings
- CAG reflex buffer loaded with all known cases
- Persistent HTTP client established to Ollama

### 2.2 Interface Layout

| Zone | Contents |
|---|---|
| **Header Bar** | System title and connection status |
| **Tool Bar** | Prompt selector, Brain Editor toggle, New Protocol button, Query Log button |
| **Main Workspace** | File upload, ingestion progress, raw JSON output, audit findings table |
| **Query Panel** | Natural language search field and narrative response display |

---

## 3. Document Ingestion

### 3.1 Uploading a Document

1. Click the file input or drag-and-drop a PDF, DOCX, or TXT file
2. Select a Mission Protocol from the dropdown
3. Click **EXECUTE MISSION**

Supported formats: PDF (including scanned via OCR fallback), DOCX, and plain TXT. The system auto-detects the best extraction method per file.

### 3.2 Ingestion Pipeline

| Step | What Happens |
|---|---|
| **1 — Extraction** | File routed to pdfplumber → OCR → PyPDF2 fallback chain. Garbled/binary output rejected automatically. |
| **2 — Identity Discovery** | Single LLM call reads first 4,000 chars to identify Plaintiff, Defendant, Appellant, Appellee, and Case Title. |
| **3 — Smart Chunking** | Document split on natural paragraph boundaries into ~3,500 character segments. Legal context never split mid-sentence. |
| **4 — Python Masking** | Zero-latency Python replaces generic role labels (e.g. "Plaintiff") with actual party names from Step 2. |
| **5 — Auditor LLM** | `sovereign-auditor` extracts 3–5 structured findings per chunk: finding, type, significance, category, impact, reference. |
| **6 — Storage** | Valid findings written to SQLite (Layer 1), indexed into FAISS (Layer 2), CAG buffer refreshed (Layer 3). |

### 3.3 Ingestion Output

After processing the UI shows:
- Case ID and resolved Case Name (auto-extracted from document header)
- Total findings count and average confidence score
- Processing latency in seconds
- Per-finding audit table: Finding / Type / Significance / Category / Impact / Reference

> **DUPLICATE PROTECTION:** If you upload the same file while it's still being processed, the system rejects the second attempt with a 409 Conflict. This prevents duplicate findings in the ledger.

---

## 4. Query Engine

The query interface is a four-layer retrieval system. Each layer is only invoked if the layer above it returns no results.

### Layer 1 — CAG Reflex Buffer *(Fastest)*

All case data held in memory. Exact or near-exact hits return instantly from RAM. No disk I/O, no LLM call.

### Layer 2 — SQLite Exact Match

FTS5 full-text search with BM25 lexical weighting against the structured findings database. Best for specific legal terms, case names, or party identifiers.

### Layer 3 — FAISS Semantic Search + Narrator Synthesis

When exact matching fails, FAISS performs dense vector search across all findings. Top 5 semantic matches are passed to `sovereign-narrator`, which synthesizes a structured HTML narrative with cited case names. Handles paraphrased, conceptual, or cross-case queries.

### Layer 4 — Global LLM Fallback

If no findings are retrieved at all, the system assembles the case list from SQLite and sends the query directly to the narrator for a best-effort grounded response.

> **QUERY TIPS:** Use specific legal terminology for fastest results (Layer 1/2). Use conceptual or paraphrased questions to leverage semantic search (Layer 3). Every query is logged with its layer hit and latency.

### Query Response Structure

| Field | Description |
|---|---|
| `query` | Your original query string |
| `layer` | Which layer answered: `cag` / `sqlite` / `faiss` / `llm` |
| `intent` | Detected type: `cag` / `exact` / `semantic` / `unstructured` |
| `results` | Array of structured findings |
| `answer` | Narrator-synthesized HTML narrative (Layer 3/4 only) |
| `latency_ms` | End-to-end response time in milliseconds |

---

## 5. Case Management

### 5.1 Case List

Each entry shows: Case ID, Case Name, source filename, chunk count, total findings, ingestion timestamp.

### 5.2 Audit Trail

Click any case to view its full chronological audit trail — every chunk processed, its segment type (ARGUMENT / CITATION / PROCEDURAL), findings extracted, and confidence score. Complete chain of custody for all extracted intelligence.

### 5.3 Deleting a Case

Delete via the trash icon. Removes all findings from SQLite, de-indexes from FAISS, and purges from CAG buffer on next refresh. Irreversible.

> **NOTE:** Deletion removes extracted findings and metadata only. The original document on disk is not touched.

---

## 6. Mission Protocols (Prompt System)

Mission Protocols are the extraction instructions given to the Auditor LLM. They define what the system looks for in each document. Create, edit, and manage protocols entirely from the UI — no file system access required.

### 6.1 Selecting a Protocol

The protocol dropdown in the Tool Bar lists all `.txt` files in the `/prompts` directory.

### 6.2 Brain Editor

Click **BRAIN EDITOR** in the Tool Bar to open an inline editor showing the current protocol's full content. Save via the Save Protocol button. Changes take effect on the next upload — no restart required.

### 6.3 Creating a New Protocol

Click **NEW PROTOCOL** to generate a timestamped template (e.g. `custom_protocol_20250619_143022.txt`) with a standard schema skeleton.

### 6.4 Protocol Schema

The Auditor expects JSON output structured as:

```json
{
  "result": [
    {
      "finding": "...",
      "type": "holding|precedent|dicta|dissent|admission|contradiction",
      "significance": "...",
      "category": "jurisdiction|evidence|constitutional|statutory|procedural|...",
      "impact": "...",
      "reference": "..."
    }
  ],
  "confidence": 0.85,
  "reasoning": "..."
}
```

| Field | Valid Values |
|---|---|
| `type` | holding, precedent, dicta, dissent, constitutional interpretation, procedural, admission, contradiction |
| `category` | jurisdiction, evidence, constitutional, statutory, procedural, contractual, admission, timeline, contradiction |
| `confidence` | Float 0.0–1.0 |
| `reference` | Case citation, statute, or document section identifier |

---

## 7. System Dashboard

Access at `/dashboard` (API) or the Dashboard button in the UI.

| Metric | Description |
|---|---|
| `total_cases` | Unique cases in the Sovereign Ledger |
| `total_findings` | Aggregate findings across all cases |
| `sqlite_hit_rate` | Ratio of queries answered by exact SQLite match (target: >0.6) |
| `avg_latency_ms` | Average query latency across last 100 queries |
| `recent_cases` | 5 most recently ingested cases |
| `recent_queries` | 10 most recent queries with layer hit and latency |
| `findings_by_type` | Count breakdown by finding type |
| `findings_by_category` | Count breakdown by category |
| `faiss` | Index size and vector dimension stats |
| `cag` | Buffer case count and memory usage |

### Telemetry Sidecar

Runs on port 8002 (localhost only). Tracks per-function call counts and avg execution time, system memory (RSS + Python heap), event loop lag, and LLM call history with token counts and tokens/sec. Not exposed to clients.

---

## 8. Query Log

Click **QUERY LOG** in the Tool Bar to view the last 50 queries. Each record shows query text, layer hit, result count, latency (ms), and timestamp.

A high LLM fallback rate indicates the corpus needs more ingestion or the protocols need tuning.

---

## 9. API Reference

All endpoints on port 8001.

| Endpoint | Description |
|---|---|
| `GET /` | Serves the main UI |
| `POST /upload` | Ingest a document. Form fields: `file`, `selected_prompt`, `is_raw_prompt` |
| `POST /query` | Natural language query. Body: `{"query": "..."}` |
| `POST /search` | Direct FAISS search. Body: `{"query": "...", "k": 5, "case_id": null}` |
| `GET /cases` | List all cases |
| `GET /cases/{id}/trail` | Full audit trail for a case |
| `DELETE /cases/{filename}` | Remove a case and all findings |
| `GET /prompts` | List all protocol files |
| `GET /prompts/{filename}` | Retrieve a protocol's content |
| `POST /prompts/save` | Save/update a protocol |
| `POST /prompts/create` | Create a new timestamped protocol template |
| `GET /dashboard` | Full system health and stats |
| `GET /query/log` | Recent query history (default: last 50) |

---


## 11. Troubleshooting

| Symptom | Fix |
|---|---|
| Engine won't start | Verify Ollama is running and both models are loaded. Check port 8001 is free. |
| PDF extracts garbled text | Engine auto-falls back to OCR. Install `pytesseract` + `poppler` for full OCR support. |
| "Mission already in progress" | Gatekeeper blocked duplicate upload. Wait for current ingestion to finish or delete the partial case first. |
| Query returns no results | Ledger may be empty. Check `/dashboard` for `total_findings` count. |
| FAISS returns stale results | Create an `ADAPTER_UPDATED.flag` file in the project directory and run any query to trigger a reload. |
| Slow ingestion | One LLM call per chunk. Monitor token throughput via telemetry sidecar at `http://localhost:8002`. |
| ngrok URL not working | Free-tier URL changes every session. Regenerate and reshare before each demo. |

### Log Locations

- **Console (stdout):** All INFO and WARNING events during ingestion and query
- **Telemetry:** `http://localhost:8002` — JSON with per-function timing and LLM call history
- **Query Log:** `/query/log` endpoint or the Query Log button in the UI

---

*AI Your Way — Confidential / For Authorized Demo Use Only*
