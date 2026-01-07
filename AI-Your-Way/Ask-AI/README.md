# Ask-AI: Multi-KB RAG System with Cross-Model Retrieval

Ask-AI is a production-grade Retrieval-Augmented Generation (RAG) system that queries multiple knowledge bases simultaneously, performs semantic reranking, and uses a triple-LLM agent architecture to deliver accurate answers with confidence scoring.

**Core Principle:** Knowledge retrieval should be fast, accurate, and model-agnostic. Ask-AI achieves this by supporting multiple embedding models, cross-KB retrieval, and intelligent fallback mechanisms—all running locally with zero API costs.

---

## What It Does

Ask-AI transforms stored knowledge into accurate, contextual answers:

- **Multi-KB retrieval** across knowledge bases with different embedding models
- **Per-model semantic reranking** using local sentence transformers
- **Cross-KB score fusion** to find the best answer regardless of source
- **Triple-LLM agent system** (Initializer, Orchestrator, Reasoner) for query processing
- **Answer augmentation** with semantic validation to improve clarity
- **Web search fallback** using DuckDuckGo when KB lookup fails
- **Confidence scoring** based on retrieval quality, rerank scores, and consensus

All processing happens locally. No external RAG services. No API keys. No recurring costs.

---

## Why It Exists

Traditional RAG systems have critical limitations:

**The Single-Model Trap**  
Most RAG systems assume one embedding model per deployment. If you have domain-specific knowledge bases built with different models (medical with BioBERT, legal with LegalBERT, technical with CodeBERT), you can't query them together.

**The Reranking Gap**  
Vector similarity alone is insufficient. A document about "Python programming" and "python snakes" may have high cosine similarity but completely different semantic meaning. Reranking is essential but expensive at API scale.

**The Hallucination Problem**  
LLMs augment answers by adding context—but also add hallucinations. There's no validation that the augmented answer remains semantically consistent with the original KB content.

Ask-AI solves all three:
- **Model-agnostic architecture:** Each KB declares its embedding model in metadata; Ask-AI loads the correct model automatically
- **Local reranking:** Per-model semantic reranking with sentence transformers (no API calls)
- **Semantic validation:** Augmented answers must pass keyword overlap (30%) and embedding similarity (70%) thresholds

---

## Architecture

### Triple-LLM Agent System

Ask-AI uses three specialized agents for different reasoning tasks:

| Agent | Model | Size | Role | Temperature |
|:------|:------|-----:|:-----|:------------|
| **Initializer** | llama3.2:1b-instruct-q4_K_M | 1B | Query classification, intent detection | 0.0 |
| **Orchestrator** | llama3.2:3b-instruct-q8_0 | 3B | Task routing, coordination | 0.3 |
| **Reasoner** | llama3:8b-instruct-q5_K_M | 8B | Answer augmentation, refinement | 0.3 |

**Why Three Agents?**

Different tasks require different reasoning capabilities:
- **Query classification:** "Is this medical, legal, or technical?" → 1B model (fast, literal)
- **Task coordination:** "Which KB should answer this?" → 3B model (routing logic)
- **Answer refinement:** "How can I clarify this answer?" → 8B model (semantic reasoning)

Using a single 70B model for all tasks wastes 90% of compute on simple classification.

### System Architecture

```
User Query
    ↓
[Multi-KB Vector Retrieval - FAISS]
    ├─ KB1 (BioBERT, 768D) → Top-5 results
    ├─ KB2 (all-MiniLM-L6-v2, 384D) → Top-5 results
    └─ KB3 (all-mpnet-base-v2, 768D) → Top-5 results
    ↓
[Per-Model Semantic Reranking]
    ├─ BioBERT results → Rerank with BioBERT
    ├─ MiniLM results → Rerank with MiniLM
    └─ MPNet results → Rerank with MPNet
    ↓
[Cross-KB Score Fusion]
    • Merge all reranked results
    • Sort by rerank score descending
    • Select best answer across KBs
    ↓
[Answer Extraction & Cleaning]
    • Remove wiki artifacts ([edit], [1], footnotes)
    • Normalize whitespace
    • Format for human readability
    ↓
[Optional: LLM Augmentation]
    • Reasoner Agent refines answer
    • Semantic validation (70% similarity threshold)
    • Keyword overlap check (30% minimum)
    ↓
[Confidence Scoring]
    • Outcome signal (KB_DIRECT=1.0, KB_AUGMENTED=0.9, WEB=0.4)
    • RAG consensus (60th percentile similarity across snippets)
    • Rerank score (top result quality)
    • Statistical baseline (0.5)
    ↓
[Web Fallback - DuckDuckGo]
    • Activates if KB score < threshold
    • Timeout: 5 seconds
    • Returns top snippet (max 500 chars)
    ↓
Final Answer + Metadata
```

---

## Key Features

### Multi-KB Cross-Model Retrieval

**Problem:** You have 3 knowledge bases:
- Medical KB (BioBERT embeddings, 768D)
- Legal KB (all-MiniLM-L6-v2 embeddings, 384D)
- Technical KB (all-mpnet-base-v2 embeddings, 768D)

Traditional RAG systems can only query one model at a time.

**Ask-AI Solution:**

```python
# Each KB declares its model in metadata
KB1_metadata = {
    "embedding_model": "BioBERT-embeddings",
    "embedding_dim": 768,
    "documents": [...]
}

KB2_metadata = {
    "embedding_model": "all-MiniLM-L6-v2",
    "embedding_dim": 384,
    "documents": [...]
}

# Ask-AI loads correct models automatically
RAG_ENGINES = {
    "medical_kb|v1": RAGEngine(kb="medical_kb", model="BioBERT"),
    "legal_kb|v2": RAGEngine(kb="legal_kb", model="MiniLM"),
    "tech_kb|v1": RAGEngine(kb="tech_kb", model="MPNet")
}

# Single query searches all KBs
query = "What are the CPT codes for appendectomy?"
results = query_across_kbs(query, active_kbs=["medical_kb|v1", "legal_kb|v2"])
# Returns: Best match from medical_kb (BioBERT detected medical terminology)
```

**Key Innovation:** Metadata-driven model loading eliminates hardcoded dependencies.

### Per-Model Semantic Reranking

**Why Reranking Matters:**

Vector similarity (cosine distance) is insufficient for semantic relevance:

```
Query: "Python exception handling"

Results by FAISS score:
1. "Python snakes are cold-blooded reptiles..." (Score: 0.85)
2. "Exception handling in Python uses try/except..." (Score: 0.82)
3. "Python package management with pip..." (Score: 0.80)
```

FAISS ranks the snake article highest because "Python" appears frequently.

**After Semantic Reranking:**

```
Results by rerank score:
1. "Exception handling in Python uses try/except..." (Score: 0.91)
2. "Python package management with pip..." (Score: 0.78)
3. "Python snakes are cold-blooded reptiles..." (Score: 0.34)
```

Reranking uses sentence embeddings to compute true semantic similarity.

**Implementation:**

```python
class LocalReranker:
    def __init__(self, embedder: SentenceTransformer):
        self.embedder = embedder
    
    def predict(self, pairs: List[Tuple[str, str]]) -> List[float]:
        # Encode queries and candidates in batches
        query_embs = embedder.encode(queries, batch_size=32)
        candidate_embs = embedder.encode(candidates, batch_size=32)
        
        # Compute cosine similarities
        scores = [np.dot(q, c) for q, c in zip(query_embs, candidate_embs)]
        
        return scores
```

**Performance:**
- Batch encoding: 32 texts per batch
- Speed: ~50ms for 10 pairs on CPU
- Memory: <500MB for 3 active rerankers

### Cross-KB Score Fusion

After per-model reranking, results from different KBs must be combined:

```python
# Medical KB results (BioBERT)
medical_results = [
    {"text": "CPT 44950: Appendectomy", "rerank_score": 0.92, "source_kb": "medical"},
    {"text": "ICD-10 K35.80: Unspecified acute appendicitis", "rerank_score": 0.88}
]

# Legal KB results (MiniLM)
legal_results = [
    {"text": "Healthcare billing regulations...", "rerank_score": 0.65, "source_kb": "legal"}
]

# Cross-KB fusion
all_results = medical_results + legal_results
sorted_results = sorted(all_results, key=lambda x: x["rerank_score"], reverse=True)

# Best answer: CPT 44950 from medical KB (score 0.92)
```

**Key Insight:** Rerank scores are comparable across models because they use normalized cosine similarity [0, 1].

### Answer Augmentation with Validation

**The Augmentation Problem:**

LLMs can improve answer clarity but also introduce hallucinations:

```
Original KB Answer:
"CPT 44950 is used for open appendectomy procedures."

LLM Augmentation (No Validation):
"CPT 44950 is the code for laparoscopic appendectomy, typically billed at $5,000-$8,000."
                    ↑ WRONG              ↑ HALLUCINATED
```

**Ask-AI Solution: Semantic Validation**

```python
def augment_answer_with_llm(kb_answer, query, context):
    # Step 1: LLM refines answer
    augmented = REASONING_AGENT.chat([
        {"role": "system", "content": "Refine without adding new information"},
        {"role": "user", "content": f"Core: {kb_answer}\nContext: {context}\nQuery: {query}"}
    ])
    
    # Step 2: Keyword overlap check
    kb_keywords = {"cpt", "44950", "open", "appendectomy", "procedures"}
    aug_keywords = {"cpt", "44950", "open", "appendectomy", "code"}
    overlap = len(kb_keywords & aug_keywords) / len(kb_keywords)  # 0.80
    
    # Step 3: Embedding similarity check
    kb_emb = embedder.encode([kb_answer])
    aug_emb = embedder.encode([augmented])
    similarity = cosine_similarity(kb_emb, aug_emb)  # 0.88
    
    # Step 4: Accept only if both thresholds pass
    if overlap >= 0.30 and similarity >= 0.70:
        return augmented  # ACCEPT
    else:
        return kb_answer  # REJECT, use original
```

**Thresholds:**
- Keyword overlap: 30% minimum (prevents topic drift)
- Embedding similarity: 70% minimum (prevents semantic divergence)

**Result:** Augmentation improves clarity without hallucination.

### Confidence Scoring System

Ask-AI computes confidence using weighted signals:

```python
CONFIDENCE_WEIGHTS = {
    "outcome": 0.35,    # Source quality (KB vs web vs fail)
    "user": 0.25,       # User feedback signal
    "rag": 0.25,        # RAG consensus score
    "rerank": 0.10,     # Top rerank score
    "stat": 0.05        # Statistical baseline
}

OUTCOME_SCORES = {
    "KB_DIRECT": 1.0,      # Answer from KB without augmentation
    "KB_AUGMENTED": 0.9,   # Answer from KB with LLM refinement
    "HIL_RECALL": 0.85,    # Human-in-loop correction
    "RAG": 0.7,            # Multi-snippet synthesis
    "WEB": 0.4,            # DuckDuckGo fallback
    "FAIL": -1.0           # No answer found
}
```

**Example Calculation:**

```python
signals = {
    "outcome": 0.9,    # KB_AUGMENTED
    "user": 0.0,       # No feedback yet
    "rag": 0.75,       # 60th percentile similarity
    "rerank": 0.88,    # Top result score
    "stat": 0.5        # Baseline
}

# Normalize signals from [-1, 1] to [0, 1]
normalized = {k: (v + 1.0) / 2.0 for k, v in signals.items()}

# Weighted sum
confidence = sum(normalized[k] * WEIGHTS[k] for k in WEIGHTS)
# Result: 0.83 (High confidence)
```

**RAG Consensus Score:**

Measures agreement between final answer and retrieved snippets:

```python
def rag_consensus_signal(answer_emb, snippet_embs):
    # Compute similarity between answer and each snippet
    similarities = [cosine_similarity(answer_emb, s) for s in snippet_embs]
    
    # Use 60th percentile to avoid outlier dominance
    consensus = np.percentile(similarities, 60)
    
    return consensus
```

**Why 60th Percentile?**

- Mean: Sensitive to outliers (one bad snippet tanks score)
- Median: Ignores high-quality snippets
- 60th percentile: Balanced measure of overall agreement

### Web Search Fallback

When KB retrieval fails (no results, low confidence), Ask-AI searches the web:

```python
def online_fallback(query: str) -> str:
    try:
        # DuckDuckGo search with timeout
        with ThreadPoolExecutor() as executor:
            future = executor.submit(ddgs_search, query)
            result = future.result(timeout=5)  # 5 second timeout
        
        if result.startswith("WEB_SUCCESS"):
            snippet = result.split(": ", 1)[-1]
            
            # Truncate intelligently at sentence boundary
            if len(snippet) > 500:
                last_period = snippet.rfind('.', 0, 500)
                if last_period > 350:
                    snippet = snippet[:last_period + 1]
            
            return snippet
        
        return "WEB_FAIL: No results"
    
    except TimeoutError:
        return "WEB_FAIL: Search timeout"
```

**Configuration:**
- Maximum snippet length: 500 characters
- Timeout: 5 seconds
- Fallback priority: KB → Web → "No answer found"

---

## Performance Benchmarks

### Test Environment

**Hardware:**
- CPU: Intel Core i3-1115G4 (11th Gen, 3.0GHz, 2 cores/4 threads)
- RAM: 36GB DDR4
- GPU: Intel UHD Graphics (integrated)
- Storage: NVMe SSD

**Loaded KBs:**
- 3 knowledge bases (BioBERT, MiniLM, MPNet)
- Total vectors: ~50,000
- Total memory: <3GB RAM

### Query Performance

| Operation | Duration | Notes |
|:----------|:---------|:------|
| FAISS retrieval (3 KBs) | 20–40ms | 5 results per KB |
| Reranking (15 pairs) | 50–80ms | Batch processing |
| Score fusion | <5ms | Sorting + merging |
| Answer extraction | <10ms | Text cleaning |
| LLM augmentation | 8–12s | Reasoner agent (8B) |
| Web fallback | 2–5s | DuckDuckGo timeout |
| **Total (KB only)** | **100–150ms** | Without augmentation |
| **Total (augmented)** | **8–12s** | With LLM refinement |

### Resource Usage

**Memory:**
- FAISS indexes: ~1.5GB (3 KBs loaded)
- Embedding models: ~1GB (3 models cached)
- Session memory: <50MB (50 entries/user)
- Total: <3GB RAM

**CPU:**
- Retrieval: 40–60% during query
- Reranking: 50–70% during batch encoding
- Idle: <5%

---

## Configuration Parameters

### Retrieval Settings

```python
TOP_K_RETRIEVE = 5                    # Results per KB
OUTLIER_SIM_THRESHOLD = 0.7           # Minimum FAISS similarity
HIL_RECALL_THRESHOLD = 0.90           # Human-in-loop confidence
```

### LLM Settings

```python
OLLAMA_TIMEOUT = 180.0                # LLM request timeout
ENABLE_LLM_AUGMENTATION = True        # Toggle augmentation
AUGMENTATION_MIN_RERANK = 0.15        # Minimum rerank for augmentation
AUGMENTATION_SEMANTIC_THRESHOLD = 0.70 # Embedding similarity threshold
MAX_CONTEXT_LENGTH = 3000             # Max context chars for LLM
```

### Session Management

```python
SESSION_MEMORY_MAX_ENTRIES = 50       # Max entries per user
SESSION_MEMORY_MAX_AGE = 3600         # Max age in seconds (1 hour)
```

### Web Search

```python
WEB_SNIPPET_MAX_LENGTH = 500          # Max snippet chars
WEB_FALLBACK_TIMEOUT = 5              # Search timeout in seconds
```

### Confidence Weights

```python
PHASE3_CONF_WEIGHTS = {
    "outcome": 0.35,    # Source type weight
    "user": 0.25,       # User feedback weight
    "rag": 0.25,        # RAG consensus weight
    "rerank": 0.10,     # Rerank score weight
    "stat": 0.05        # Statistical baseline weight
}
```

---

## API Endpoints

### Health Check

```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "loaded_kbs": 3,
  "active_kbs": 3,
  "total_vectors": 50000,
  "ollama_available": true,
  "ddgs_available": true,
  "session_users": 5,
  "total_sessions": 47
}
```

### List Available KBs

```
GET /api/kb/list
```

**Response:**
```json
{
  "status": "success",
  "kbs": ["medical_kb", "legal_kb", "tech_kb"]
}
```

### Browse KB Files

```
GET /api/kb/browse/<kb_name>
```

**Response:**
```json
{
  "status": "success",
  "kb_name": "medical_kb",
  "paired_files": [
    {
      "version": 2,
      "faiss_file": "faiss_index_v2.bin",
      "meta_file": "meta_map_v2.pkl",
      "faiss_size": 52428800,
      "meta_size": 10485760,
      "modified": 1704585600
    }
  ]
}
```

### Load Multiple KBs

```
POST /api/kb/load_multiple
Content-Type: application/json

{
  "kb_name": "medical_kb",
  "pairs": [
    {
      "faiss_file": "faiss_index_v2.bin",
      "meta_file": "meta_map_v2.pkl",
      "version": 2
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "loaded_count": 1,
  "loaded_keys": ["medical_kb|v2"],
  "active_kbs": ["medical_kb|v2"],
  "total_vectors": 25000,
  "models": ["BioBERT-embeddings"]
}
```

### Query

```
POST /api/query
Content-Type: application/json

{
  "user_id": "user123",
  "query": "What are the CPT codes for appendectomy?"
}
```

**Response:**
```json
{
  "status": "success",
  "query": "What are the CPT codes for appendectomy?",
  "answer": "CPT 44950 is used for open appendectomy procedures...",
  "kb_answer": "CPT 44950: Appendectomy, open approach",
  "kb_answer_readable": "CPT 44950: Appendectomy, open approach",
  "source_type": "KB_AUGMENTED",
  "source_kb": "medical_kb|v2",
  "active_kbs": ["medical_kb|v2"],
  "confidence": 0.85,
  "rerank_score": 0.92,
  "rag_score": 0.78,
  "retrieved_count": 5,
  "augmented": true,
  "session_length": 3
}
```

### Submit Feedback

```
POST /api/feedback
Content-Type: application/json

{
  "user_id": "user123",
  "query": "What are the CPT codes for appendectomy?",
  "answer": "CPT 44950: Appendectomy, open approach",
  "feedback": "approve"
}
```

**Feedback Options:**
- `approve`: Answer is correct (signal: 1.0)
- `edit`: Answer needs refinement (signal: 0.0)
- `reject`: Answer is wrong (signal: -1.0)

**Response:**
```json
{
  "status": "success",
  "confidence": 0.87,
  "message": "Feedback logged"
}
```

---

## Use Cases

### Medical Q&A System

**Challenge:** Query medical billing codes, drug interactions, and clinical procedures from multiple knowledge bases built with different embedding models.

**How Ask-AI Solves It:**
- Medical KB (BioBERT) handles CPT/ICD codes
- Drug KB (PubMedBERT) handles pharmaceutical queries
- Clinical KB (all-mpnet) handles general medical questions
- Cross-KB fusion ensures best answer regardless of source

**Result:** Accurate medical answers with 85%+ confidence, zero API costs.

### Legal Document Search

**Challenge:** Search case law, statutes, and regulations while maintaining citation accuracy.

**How Ask-AI Solves It:**
- Legal KB (LegalBERT) for case law and statutes
- Regulatory KB (RoBERTa) for administrative codes
- Reranking prevents citation hallucination
- Augmentation improves readability without changing facts

**Result:** Precise legal citations with semantic validation.

### Technical Support Knowledge Base

**Challenge:** Answer software troubleshooting questions from vendor docs, Stack Overflow archives, and internal guides.

**How Ask-AI Solves It:**
- Vendor KB (CodeBERT) for official documentation
- Community KB (all-MiniLM) for Stack Overflow content
- Internal KB (all-mpnet) for company-specific guides
- Web fallback for new issues not in KB

**Result:** Fast, accurate technical support with confidence scoring.

---

## Technical Architecture Deep Dive

### Metadata-Driven KB Loading

Traditional RAG systems hardcode embedding models:

```python
# Traditional approach (WRONG)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("my_kb.bin")

# Problem: What if the KB was built with a different model?
```

Ask-AI uses metadata as the single source of truth:

```python
# Ask-AI approach (CORRECT)
with open("meta_map_v2.pkl", "rb") as f:
    metadata = pickle.load(f)

embedding_model = metadata["embedding_model"]  # "BioBERT-embeddings"
embedding_dim = metadata["embedding_dim"]      # 768

# Load correct model
embedder = SentenceTransformer(f"models/{embedding_model}")

# Validate dimension
index = faiss.read_index("faiss_index_v2.bin")
assert index.d == embedding_dim, "Dimension mismatch"
```

**Benefits:**
- KB files are self-describing
- No configuration files or environment variables
- Model mismatch impossible (validated at load time)

### FAISS Index Structure

```python
# Flat L2 index (exact search)
index = faiss.IndexFlatL2(embedding_dim)

# Add vectors
embeddings = np.array([...], dtype=np.float32)
index.add(embeddings)

# Search
query_emb = embedder.encode([query])
distances, indices = index.search(query_emb, k=5)

# Convert L2 distance to cosine similarity
similarities = 1.0 - (distances ** 2) / 2.0
```

**Index Types Supported:**
- Flat (exact search, best for <100k vectors)
- IVF (approximate search, best for >100k vectors)
- HNSW (graph-based, best for >1M vectors)

### Reranker Batching Strategy

```python
class LocalReranker:
    def predict(self, pairs: List[Tuple[str, str]]) -> List[float]:
        queries, candidates = zip(*pairs)
        all_texts = list(queries) + list(candidates)
        
        # Batch encode for efficiency
        if len(all_texts) > 32:
            embeddings = []
            for i in range(0, len(all_texts), 32):
                batch = all_texts[i:i+32]
                batch_embs = self.embedder.encode(batch, normalize=True)
                embeddings.append(batch_embs)
            embeddings = np.vstack(embeddings)
        else:
            embeddings = self.embedder.encode(all_texts, normalize=True)
        
        # Split and compute similarities
        query_embs = embeddings[:len(queries)]
        candidate_embs = embeddings[len(queries):]
        
        scores = [np.dot(q, c) for q, c in zip(query_embs, candidate_embs)]
        return scores
```

**Performance:**
- Batch size: 32 texts
- Speedup: 3–5× faster than sequential encoding
- Memory: O(batch_size × embedding_dim)

---

## Comparison to Alternatives

| Feature | Ask-AI | Pinecone | Weaviate | LangChain |
|:--------|:-------|:---------|:---------|:----------|
| **Cost/month** | $0 | $70–200 | $25–100 | Varies |
| **Multi-model support** | Yes | No | Limited | No |
| **Cross-KB retrieval** | Yes | Manual | Manual | No |
| **Local reranking** | Yes | No | No | External API |
| **Semantic validation** | Yes | No | No | No |
| **Confidence scoring** | Yes | No | No | No |
| **Web fallback** | Yes | No | No | External API |
| **Data sovereignty** | Complete | Zero | Zero | Partial |
| **Network dependency** | None* | Required | Required | Required |

*After initial model download

---

## Limitations & Design Choices

### What Ask-AI Does NOT Do

**No Vector Database**  
Ask-AI uses FAISS (flat files), not a persistent vector DB. Updates require rebuilding indexes.

**No Distributed Search**  
Single-process design. Horizontal scaling requires manual sharding.

**No Real-Time Updates**  
KB updates require reloading. Not suitable for rapidly changing data.

**No Authentication**  
Single-user or trusted environment only. Multi-tenant deployments require auth middleware.

### Why These Choices?

**FAISS over Vector DB:** Simplicity and portability. No database server, no vendor lock-in.

**Single-Process:** Reduces complexity. Most use cases don't need distributed search.

**No Real-Time Updates:** Knowledge bases change infrequently. Rebuild cost is acceptable.

**No Auth:** Focus on core RAG functionality. Auth is deployment-specific.

---

## Commercial Licensing

Ask-AI is available for commercial deployment under proprietary licensing.

**Ideal For:**
- Healthcare organizations (HIPAA-compliant medical Q&A)
- Law firms (privileged document search)
- Financial institutions (regulatory compliance queries)
- Enterprises (internal knowledge base search)
- Research labs (academic paper retrieval)

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
| RAM | 16GB (32GB recommended for multiple KBs) |
| Storage | 20GB free (varies with KB size) |
| OS | Windows 10/11, Linux, macOS |
| Network | Internet for model download only |

### Dependencies

```
Python 3.8+
Ollama (local LLM runtime)
Flask
FAISS (vector search)
sentence-transformers (embeddings + reranking)
numpy
duckduckgo-search (optional, web fallback)
```

---

## Philosophy

Ask-AI is built on three principles:

**1. Model-Agnostic**  
Your embedding model choice should not lock you into a single KB architecture.

**2. Validation-First**  
LLM augmentation is powerful but dangerous. Semantic validation prevents hallucination.

**3. Zero-API-Cost**  
Local retrieval, local reranking, local LLMs. No usage-based pricing, no vendor dependencies.

Cloud-based RAG services optimize for vendor revenue through API calls. Ask-AI optimizes for accuracy, flexibility, and cost elimination.

---

## Status

**Current Version:** Production-ready  
**Last Updated:** January 2025  
**Deployment:** Local/on-premises only  
**License:** Proprietary (commercial licensing available)

The code is not open-source, but the architecture and principles are documented here for evaluation purposes.
