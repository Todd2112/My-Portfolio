# Ask-AI — Multi-Knowledge-Base RAG System

A local multi-knowledge-base RAG system with model-specific retrieval, semantic reranking, answer validation, and explainable scoring.

Ask-AI can query knowledge bases built with different embedding models, combine the results, optionally augment the retrieved answer with a local language model, and return source metadata and intermediate scoring signals.

No cloud API is required during normal operation. An optional web fallback can be enabled when external search is acceptable.

→ [Code Snippets](snippets/)

---

## What This Demonstrates

- Designing RAG systems around heterogeneous embedding models
- Loading and validating versioned FAISS indexes
- Detecting metadata, dimension, and vector-count mismatches
- Separating retrieval, reranking, generation, validation, and response formatting
- Combining results from multiple knowledge bases
- Using local models for classification, routing, and answer augmentation
- Implementing fallback behavior when retrieval or augmentation fails
- Measuring latency and memory usage on constrained hardware
- Returning source metadata and intermediate scoring signals

---

## The Problem

A basic RAG implementation often assumes:

- One embedding model for the entire deployment
- One vector index
- Raw vector similarity is sufficient for ranking
- Generated answers can be returned without validation
- Confidence can be inferred from a single similarity score

Ask-AI explores a more explicit architecture:

| Problem | Basic RAG Approach | Ask-AI Approach |
|:--|:--|:--|
| Multiple domains | One shared embedding model | Each knowledge base declares its own model |
| Metadata errors | Fail later during querying | Validate model dimensions and vector counts at load time |
| Ranking quality | Use FAISS similarity alone | Apply model-specific semantic reranking |
| Cross-KB retrieval | Manually combine results | Retrieve, annotate, normalize, and fuse results |
| LLM augmentation | Return generated text directly | Validate augmented output before returning it |
| Answer quality | One similarity score | Composite score using multiple signals |
| External search | Always or never use web search | Optional fallback only when local retrieval fails |

---

## Architecture

### Eight-Stage Query Pipeline

```text
User Query
    |
    v
[1. Multi-KB Retrieval]
    Each knowledge base is queried with its own embedding model.
    Results are annotated with source_kb and kb_model.
    |
    v
[2. Per-Model Reranking]
    Results are grouped by embedding model.
    Each group is reranked using its corresponding LocalReranker.
    |
    v
[3. Cross-KB Score Fusion]
    Reranked groups are combined and ordered.
    Scores are normalized for cross-KB ranking.
    |
    v
[4. Answer Extraction]
    The strongest retrieved answer is selected.
    Formatting artifacts and unwanted markup are removed.
    |
    v
[5. Optional LLM Augmentation]
    A local reasoning model may improve clarity.
    The result is checked against the retrieved answer.
    |
    v
[6. Composite Answer Scoring]
    Retrieval, reranking, outcome, and feedback signals are combined.
    |
    v
[7. Optional Web Fallback]
    External search runs only when local retrieval produces no answer.
    |
    v
[8. Structured Response]
    Answer, source metadata, scoring signals, and status are returned.
```

→ Query pipeline snippet [blocked]

### Local Agent System

| Agent | Model | Approx. Size | Temperature | Role |
|:--|:--|:--:|:--:|:--|
| Initializer | `llama3.2:1b-instruct-q4_K_M` | 1B | 0.0 | Query classification |
| Orchestrator | `llama3.2:3b-instruct-q8_0` | 3B | 0.3 | Task routing |
| Reasoner | `llama3:8b-instruct-q5_K_M` | 8B | 0.3 | Answer augmentation |

The models can be replaced independently. The architecture does not require one model to handle every operation.

## Key Features

### Metadata-Driven Knowledge-Base Loading

Each knowledge base declares its embedding model and vector dimension in metadata rather than relying on scattered configuration values.

Example:

```yaml
metadata:
    embedding_model = "BioBERT-embeddings"
    embedding_dim   = 768

loader validates:
    FAISS index dimension == 768
    model output dimension == 768
    document count == vector count
```

Mismatches raise an error during loading instead of producing confusing query-time behavior.

→ Metadata-driven loading [blocked]

### Per-Model Semantic Reranking

FAISS similarity is useful for candidate retrieval, but it may not be sufficient as the final relevance signal.

Ask-AI groups retrieved results by embedding model and applies a corresponding local reranker to each group. Reranker instances are shared between knowledge bases that use the same model to avoid unnecessary memory use.

The implementation also supports batched encoding to reduce repeated model overhead.

→ Local reranker [blocked]

### Augmentation Validation Gate

Local language models can make retrieved answers clearer, but they can also introduce unsupported details.

Before an augmented answer is accepted, it is compared with the original retrieved answer using:

- Keyword overlap
- Embedding similarity

If the augmented response fails either configured threshold, the original knowledge-base answer is returned instead.

```text
keyword overlap       >= 30%
embedding similarity  >= 70%
```

These checks reduce topic drift but do not prove factual correctness. Similarity is not the same as truth.

→ Augmentation validation [blocked]

### RAG Consensus Scoring

The system compares the final answer with retrieved snippets and uses a percentile-based score to estimate retrieval agreement.

The current implementation uses the 60th percentile:

- Mean can be reduced by one weak or unrelated result
- Median may ignore useful high-scoring evidence
- The 60th percentile provides a configurable compromise

This is a retrieval-agreement signal, not a calibrated probability of correctness.

→ RAG consensus scoring [blocked]

### Composite Answer Scoring

Ask-AI combines several signals into a single composite answer-quality score.

| Signal | Weight | Description |
|:--|--:|:--|
| Outcome type | 0.35 | Direct KB answer, augmented answer, web result, or failure |
| User feedback | 0.25 | Approval, edit, or rejection |
| RAG consensus | 0.25 | Agreement between the answer and retrieved material |
| Rerank score | 0.10 | Semantic score of the top retrieved result |
| Baseline | 0.05 | Fixed baseline contribution |

Signals are normalized before weighting so that negative outcomes can reduce the final score.

The current baseline is fixed at 0.5. It is included for architectural completeness, but it is not statistical evidence. A production system should replace it with a measured signal such as historical accuracy, source freshness, or calibration data.

The resulting value should be interpreted as a composite answer-quality score, not a certified probability of correctness.

→ Composite scoring [blocked]

### Optional Web Fallback

Web search is used only when local knowledge-base retrieval produces no answer.

The fallback includes:

- A five-second timeout
- Sentence-boundary truncation
- A source label of `WEB`
- Separate handling from local KB responses

For strictly offline or sensitive deployments, the fallback can be disabled.

## Performance Measurements

**Test hardware:**

- Intel Core i3-1115G4, 11th generation
- 36 GB RAM
- Integrated graphics

**Test configuration:**

- Three knowledge bases
- Approximately 50,000 vectors total
- Approximately 3 GB memory usage

| Operation | Observed Duration |
|:--|:--|
| FAISS retrieval across three KBs | 20–40 ms |
| Reranking 15 candidate pairs | 50–80 ms |
| Cross-KB score fusion | Less than 5 ms |
| Answer extraction and cleaning | Less than 10 ms |
| Local LLM augmentation | 8–12 seconds |
| Web fallback | 2–5 seconds |
| Total without augmentation | Approximately 100 ms |
| Total with augmentation | Approximately 10 seconds |

These are observed measurements from a local test configuration, not universal performance guarantees.

Measurements should be interpreted with the following context:

- Models were loaded locally
- Results depend on document count and candidate count
- Performance varies by embedding model and hardware
- LLM timings depend heavily on model size and quantization
- Network latency affects web fallback timing

## Resource Usage

- FAISS indexes: approximately 1.5 GB
- Cached embedding models: approximately 1 GB
- Session memory: less than 50 MB
- Recurring API cost during local operation: $0

The local cost estimate excludes hardware, electricity, storage, maintenance, monitoring, and engineering time.

## Cost Model

| Approach | Example Monthly Cost | Example Annual Cost |
|:--|:--|:--|
| Managed vector database plus hosted LLM | $160–400 | $1,920–4,800 |
| Ask-AI during local operation | $0 recurring API cost | $0 recurring API cost |

Actual costs depend on traffic, model selection, prompt size, output size, hardware, and provider pricing.

Local deployment may reduce recurring API expenses, but it transfers costs to hardware, operations, maintenance, and engineering.

## API Endpoints

```text
GET  /api/health
     System health and loaded knowledge-base count

GET  /api/kb/list
     Available knowledge-base directories

GET  /api/kb/browse/<kb>
     Versioned FAISS and metadata file pairs

POST /api/kb/load_multiple
     Load one or more knowledge bases using metadata validation

GET  /api/kb/list_loaded
     Currently loaded knowledge bases and metadata

POST /api/kb/unload
     Remove a knowledge base from memory

POST /api/query
     Main query endpoint

POST /api/feedback
     Record approve, edit, or reject feedback
```

## Example Response

```json
{
  "status": "success",
  "answer": "CPT 44950 is associated with an open appendectomy procedure.",
  "source_type": "KB_AUGMENTED",
  "source_kb": "medical_kb|v2",
  "confidence": 0.85,
  "rerank_score": 0.92,
  "rag_score": 0.78,
  "augmented": true
}
```

The score is a composite application signal. It should not be interpreted as a guarantee of correctness or as a substitute for professional review.

## Setup

### 1. Install Ollama and pull the models

```bash
ollama pull llama3.2:1b-instruct-q4_K_M
ollama pull llama3.2:3b-instruct-q8_0
ollama pull llama3:8b-instruct-q5_K_M
```

### 2. Install dependencies

```bash
pip install flask faiss-cpu sentence-transformers numpy
```

Optional web fallback:

```bash
pip install duckduckgo-search
```

### 3. Configure paths

Edit the `KB_ROOT` and `MODELS_ROOT` values in `ask_ai.py`.

### 4. Start the API

```bash
python ask_ai.py
```

The API will be available at:

```text
http://localhost:8001
```

### 5. Load a knowledge base

```bash
curl -X POST http://localhost:8001/api/kb/load_multiple \
  -H "Content-Type: application/json" \
  -d '{
    "kb_name": "my_kb",
    "pairs": [
      {
        "faiss_file": "faiss_index_v1.bin",
        "meta_file": "meta_map_v1.pkl",
        "version": 1
      }
    ]
  }'
```

## Hardware Requirements

| Component | Minimum | Recommended |
|:--|:--|:--|
| CPU | Intel i3 11th generation or Ryzen 3 | Intel i5 or better |
| RAM | 16 GB | 32 GB or more |
| Storage | 20 GB SSD | NVMe SSD with additional capacity |
| GPU | Not required | Dedicated GPU for faster inference |
| Network | Required for initial model download | Not required during local operation |

Actual requirements depend on:

- Model size
- Quantization
- Number of loaded knowledge bases
- Document volume
- Concurrent users
- Target response time

## Security and Data Flow

During normal local operation:

```text
User Query
    |
    v
Flask API on localhost:8001
    |
    +--> Local FAISS indexes
    |
    +--> Local embedding models
    |
    +--> Ollama on localhost:11434
```

The optional web fallback is the only external network operation described by this project. It should be disabled when queries and documents must remain offline.

A production deployment would still require appropriate:

- Authentication
- Authorization
- Network controls
- Logging and monitoring
- Backup and recovery procedures
- Secrets management
- Data-retention policies
- Dependency and model-update procedures

## Limitations

- Local inference may be slower than hosted APIs.
- Retrieval quality depends on document quality, chunking, metadata, and model choice.
- Cross-model scores are normalized for ranking but may not be perfectly calibrated.
- Semantic similarity does not establish factual correctness.
- The validation gate can reject useful answers or accept plausible but incorrect answers.
- Multiple embedding models increase memory usage.
- Web fallback must be disabled for strictly offline deployments.
- The system currently assumes trusted local access to the API.
- Production use requires additional security, monitoring, testing, and operational controls.
- Medical, legal, financial, and compliance-related outputs require qualified professional review.

## What This Could Be Used For

Potential applications include:

- Internal document search
- Private knowledge assistants
- Research-paper retrieval
- Technical documentation search
- Local compliance-document exploration
- Domain-specific question answering
- Document classification and routing
- Prototypes for private enterprise AI systems

This project is an engineering system and research platform, not a compliance certification or professional decision-making tool.

## Contract Work

I am available for contract work involving:

- Private RAG systems
- Document ingestion and OCR
- Local LLM deployment
- Retrieval and answer-quality evaluation
- Knowledge-base architecture
- Inference and memory optimization
- AI application debugging
- Prototype-to-production engineering
- Offline or restricted-network AI workflows

A typical initial engagement could include:

- Reviewing the existing workflow and data
- Building a small working prototype
- Creating a representative evaluation set
- Measuring retrieval quality, latency, and resource usage
- Documenting the recommended architecture
- Identifying production risks and next steps

## Project Status

- Deployment: Local or on-premises
- External API requirement: None during normal operation
- License: Proprietary
- Full script: Not currently open source
- Code snippets: Available for evaluation

The system is available for review, adaptation, and custom deployment.

## Contact

For contract engineering, technical audits, prototypes, or deployment discussions:

- Email: realtodd@yahoo.com
- GitHub: Todd2112
- LinkedIn: Todd

When contacting me, include:

- The type of documents or data involved
- The workflow you want to improve
- Whether local or private deployment is required
- Approximate document volume
- Expected number of users
- Desired response time
- Hardware or infrastructure constraints

