

# Local AI for PDF, Legal Briefs —No APIs, No Data Leaks, No Compromises.

## 100% Local Legal Engine
**High-Memory Local RAG for Instant Case Recall**

**legal PDF** is a localized, air-gapped discovery engine designed to transform massive, non-searchable legal archives into high-fidelity semantic databases. By leveraging a high-RAM, low-core architecture (optimized for i3/36GB RAM), this system provides deterministic recall for senior litigators without the privacy risks or subscription costs of cloud-based APIs.

![Sovereign Discovery Interface](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/Sovereign%20Legal%20Engine/worlflow.jpg)

---

### Performance Audit: Bench-Tested Ingestion
The following data represents a live stress test of the `Legal Engine` pipeline using a 17-segment high-complexity legal filing (*Marbury v. Madison*).

#### 1. Ingestion Efficiency (The "Shredding" Phase)
The engine utilizes a defensive fallback chain to ensure text fidelity before embedding.
* **Average Segment Speed:** ~75 seconds per chunk.
* **Deep Processing:** High-complexity segments (e.g., Segments 7, 14) are automatically allocated additional compute (~115s) for high-fidelity embedding.
* **Optimization:** Linear efficiency gains observed on standard segments, finishing in as little as **36.63s**.

#### 2. Semantic Database Construction
Post-ingestion, the system performs a multi-layer sync to ensure data is court-ready:
* **TF-IDF Backfill:** 35 unique legal findings weighted and cross-indexed.
* **FAISS Synchronization:** Vector embeddings synced for sub-millisecond semantic retrieval.
* **CAG Buffer Refresh:** 100% of findings stored in memory for **Instant Recall**.

#### 3. Query Performance (The "Instant Recall" Phase)
* **Search Latency:** Generated a complex judicial brief in **~70 seconds**.
* **Zero Data Leakage:** All requests routed to `localhost:11434`—confirming the session remained entirely air-gapped.

---

### Technical Audit Trail (Raw Logs)
```text
INFO:     MISSION STARTED: Marbury v. Madison [case_id:1] | 17 Segments
2026-05-26 10:00:43 - INFO - Processing chunk 1 (Depth 0)
2026-05-26 10:02:30 - httpx - INFO - api/generate "HTTP/1.1 200 OK"
Segment 1 finished in 112.69s

2026-05-26 10:08:08 - INFO - Processing chunk 7 (Depth 0)
Segment 7 finished in 121.68s [COMPLEX PRECEDENT DETECTED]

2026-05-26 10:20:07 - INFO - Processing chunk 15 (Depth 0)
Segment 15 finished in 36.63s [OPTIMIZED]

2026-05-26 10:23:02 - legal_db - INFO - TF-IDF backfill complete: 35 findings weighted.
2026-05-26 10:23:02 - legal_faiss - INFO - FAISS meta synced from DB.
2026-05-26 10:23:02 - legal_cag - INFO - CAG buffer refreshed: 1 cases, 35 findings in memory.
2026-05-26 10:25:00 - httpx - INFO - api/generate "HTTP/1.1 200 OK" [QUERY SUCCESS]
```


Core Engineering Features
Parallel Dual-Agent Pipeline

To eliminate context drift, reasoning is decoupled into specialized local agents:

    The Auditor (Llama 3.2 3B): Clinical extraction of Holdings, Rules, and Precedents into structured JSON.

    The Narrator (Llama 3.2 1B): Synthesis of findings into strategic briefs and keyword highlighting.

Logic Store (End-User Programmability)

A dedicated configuration layer allows users to define the "Mission Profile" for each case. By committing new logic to the store, the engine recalibrates its extraction priorities for deposition summaries, contract audits, or sentencing mitigation.
Hardware Configuration & Optimization

This build is specifically optimized for high-memory environments where CPU cores are limited, ensuring the i3 is never bottlenecked by memory-swap operations.

    Processor: Intel i3 (4 Cores)

    Memory: 36GB RAM (Enables high-capacity FAISS index caching and large-scale metadata buffering)

    Inference: Ollama (Llama 3.2 4-bit Quantized)

    Retrieval: FAISS + SQLite (Metadata anchoring)


   
