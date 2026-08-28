# AI Engineering Portfolio

I build local-first AI systems for organizations that need practical document intelligence, knowledge retrieval, and LLM workflows without sending sensitive data to third-party model APIs.

My work focuses on:

- Local LLM deployment and model routing
- Document ingestion, OCR, extraction, and classification
- Retrieval-augmented generation across multiple knowledge bases
- LLM evaluation and output validation
- Persistent, disk-backed application memory
- Cost-conscious systems that run on consumer hardware

These projects are designed for private deployments, prototypes, internal tools, and custom engineering work.

---

## Featured Projects

### AI-Your-Way — Local AI Assistant with Persistent Memory

A local coding assistant built around multiple language models selected according to task complexity.

The system separates lightweight classification and memory tasks from more demanding code-generation tasks. Conversation history, learned patterns, and project context are stored locally in JSONL files so they can be inspected, backed up, and reused across sessions.

#### Current measurements

- Classification response time: approximately 4–6 seconds
- Code-generation response time: approximately 10–20 seconds
- Test hardware: Intel i3 laptop, 36 GB RAM, integrated graphics
- API usage: none during local operation
- Storage format: human-readable JSONL

#### Technical components

- Three local language models with task-specific prompts
- Task-based model routing
- Retrieval- and pattern-based memory
- Persistent project context
- AST and style checks for generated code
- Output validation and hallucination checks
- Local configuration and data storage

[View the AI-Your-Way documentation](./AI-Your-Way)

---

### AI-Train — Document Ingestion Pipeline

A document-processing pipeline for preparing PDFs, Word documents, HTML pages, and text files for downstream search and RAG applications.

The pipeline uses extraction fallbacks when source documents contain malformed, scanned, or otherwise unusable text.

#### Features

- PDF extraction with multiple fallback paths
- OCR for scanned or garbled documents
- Word, HTML, and plain-text ingestion
- Automatic document classification
- Summarization and link analysis
- Smart chunking and goal-based filtering
- Same-domain BFS web crawling
- Thread-safe JSONL persistence
- Chunk relationship tracking
- Keyword fallback when LLM classification is unavailable

#### Domain-oriented processing

The system includes classification logic for document categories such as:

- Healthcare
- Legal
- Technical documentation
- Research material
- General business content

Domain detection is not a compliance certification. Production deployments require appropriate security controls, access management, auditing, retention policies, and organizational procedures.

[View the AI-Train documentation](./AI-Train)

---

### Ask-AI — Multi-Knowledge-Base RAG

A retrieval-augmented generation system that searches multiple knowledge bases built with different embedding models.

This makes it possible to keep domain-specific indexes—for example, medical, legal, or general-purpose content—and query them together while preserving model-specific retrieval and reranking.

#### Features

- Simultaneous retrieval across multiple knowledge bases
- Support for different embedding models
- Per-index semantic reranking
- Cross-knowledge-base score fusion
- Confidence scoring
- Semantic validation of generated answers
- Metadata-driven model loading
- Optional web fallback
- Local sentence-transformers integration

#### Current measurements

- Knowledge-base retrieval: approximately 100–150 ms
- Retrieval with LLM augmentation: approximately 8–12 seconds
- Test configuration: three or more indexes with separate embedding models

[View the Ask-AI documentation](./Ask-AI)

---

## Engineering Approach

### Use the smallest model that can do the job

Classification, filtering, and routing do not always require a large reasoning model. These systems experiment with task-specific model selection so that simple operations use fewer resources while more complex tasks can use larger local models.

### Keep application memory under your control

Conversation history, project context, and learned patterns are stored locally in inspectable formats. This makes data easier to back up, migrate, debug, and remove.

Persistent storage does not mean unlimited usable context. The application still needs retrieval, summarization, and context-management strategies as the stored dataset grows.

### Measure retrieval and answer quality

A generated answer is not automatically a good answer. Retrieval results and generated responses should be tested against representative questions, expected sources, latency targets, and failure cases.

The projects use combinations of:

- Keyword checks
- Embedding similarity
- Source validation
- Confidence thresholds
- Structured output checks
- Code parsing and AST validation

Thresholds are configuration choices, not guarantees of correctness.

### Prefer model-agnostic components

The retrieval systems are designed to support different embedding models, local runtimes, and knowledge bases. This allows the deployment to be adapted to the available hardware and the requirements of a particular domain.

---

## Why Local-First AI?

Local deployment can be useful when a system needs:

- Reduced dependence on external API availability
- More predictable operating costs
- Lower data exposure to third-party model providers
- Operation in restricted or offline environments
- Direct control over models, storage, and infrastructure
- The ability to inspect and modify the application stack

Local systems also have tradeoffs:

- Hardware must be purchased and maintained
- Larger models may require substantial memory or a GPU
- Inference can be slower than cloud services
- Updates, monitoring, backups, and security become the operator's responsibility

The right architecture depends on the workload, privacy requirements, latency target, budget, and operational environment.

---

## Cost Model

For a representative local deployment:

### Example cloud scenario

- Estimated API spend: approximately $90/month
- Estimated two-year API cost: approximately $2,160
- Actual cost depends on model, traffic, prompt size, output size, and provider pricing

### Example local scenario

- Example hardware cost: approximately $700 one time
- API spend during local operation: $0
- Estimated two-year hardware cost: approximately $700
- Does not include electricity, maintenance, storage, engineering, or support

The potential break-even point depends on actual usage and hardware costs. In one project scenario, the estimated break-even point was approximately 7.8 months.

These figures are examples, not universal cost guarantees.

---

## Other Projects

Additional experiments and proof-of-concept work include:

- **Web Keyword Crawler** — HTML parsing and trend detection
- **Reasoning AI Chatbot** — Decision-making with intermediate representations
- **Visual Data Pipeline** — Identity-preserving image generation with LoRA
- **PDF Teacher RAG** — Offline document question-answering
- **Business Solutions Suite** — Content, SEO, and social-media automation tools

[View the project archive](./)

---

## Available Contract Work

I am available for contract work involving:

- Private RAG prototypes
- Document ingestion and OCR pipelines
- Local LLM installation and deployment
- Retrieval and answer-quality evaluation
- AI application debugging
- Model routing and inference optimization
- Prototype-to-production engineering
- Internal knowledge assistants
- Custom document-processing workflows

A typical initial engagement could include:

1. Reviewing the current workflow and data
2. Building a small working prototype
3. Creating an evaluation set
4. Measuring retrieval quality, latency, and resource usage
5. Documenting the recommended architecture
6. Identifying production risks and next steps

I am particularly interested in projects where sensitive documents, recurring API costs, limited connectivity, or infrastructure control are important considerations.

---

## Technology

### Core

- Python 3.8+
- Flask
- Ollama
- FAISS
- sentence-transformers
- NumPy
- PyTorch

### Document and web processing

- pdfplumber
- PyPDF2
- pytesseract
- python-docx
- BeautifulSoup4
- duckduckgo-search

### Typical hardware

- Minimum test configuration: Intel i3, 16 GB RAM, 50 GB storage
- Recommended: Intel i5 or better, 32 GB RAM, NVMe SSD
- Optional: Dedicated GPU for faster inference and larger models

Actual requirements depend on model size, quantization, document volume, concurrency, and latency expectations.

---

## Contact

For contract engineering, prototypes, technical audits, or deployment discussions:

- Email: `realtodd@yahoo.com`
- GitHub: [Todd2112](https://github.com/Todd2112)
- LinkedIn: Todd

Please include:

- The type of documents or data involved
- The workflow you want to improve
- Whether local or private deployment is required
- Approximate document volume
- Expected users and response time
- Any hardware or infrastructure constraints

---

## Project Status

These projects are active engineering work and experiments. They are available for review, adaptation, and custom deployment.

They should be evaluated for the specific workload and deployment environment rather than treated as universal production solutions.
