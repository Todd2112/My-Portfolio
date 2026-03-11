# my_coder.py — Local AI Coding Assistant with Hybrid RAG/CAG Memory

A fully local AI coding assistant that solves the context window problem by splitting memory into
two layers: RAG for semantic retrieval and CAG for pattern learning. Three purpose-trained LLM
personas handle generation, validation, and routing — each with sampling parameters tuned to
their role.

**No context loss. No hallucinations persisted to memory. No cloud APIs. No recurring costs.**

→ [Model Architecture & Three-Brain Design](MODEL_ARCHITECTURE.md)  
→ [Code Snippets](snippets/)

---

## The Problem It Solves

Standard LLM coding assistants forget everything when the context window fills or the session
ends. Re-explaining your codebase every session wastes time and produces inconsistent output.
Larger context windows help but don't eliminate the problem — they move the ceiling, not remove it.

`my_coder.py` removes the ceiling entirely by never relying on the context window for memory.
Accepted code is indexed into a persistent vector store (RAG) and a pattern log (CAG). Every
future request pulls relevant context from those stores rather than from conversation history.

**The three structural failures this addresses:**

| Problem | Cloud LLM Behavior | This System |
|:--------|:-------------------|:------------|
| Context amnesia | State lost after session ends | Persistent vault survives indefinitely |
| Hallucinated code | Bad output stored in history | Hallucination gate blocks persistence |
| Compute waste | Every task hits a 175B model | 3 models, routed by task complexity |

---

## Architecture Overview

```
User Input
    ↓
[Keyword Bypass Layer]       ← deterministic routing, no LLM call needed
    ↓ (ambiguous input only)
[MAVERICK — 1B Organizer]    ← intent classification (temp 0.3)
    ↓
┌──────────────────┬─────────────────┬─────────────────┐
│ SOVEREIGN_CODER  │   RAG Retrieve  │ FORENSIC_AUDITOR│
│ Code generation  │   Vector search │ Code validation │
│ (7B, temp 0.2)   │                 │ (7B, temp 0.0)  │
└──────────────────┴─────────────────┴─────────────────┘
    ↓
[Hallucination Gate]         ← 5-layer confidence scoring, AST validation
    ↓ (confidence ≥ 0.6 only)
[The Vault]                  ← CAG pattern log + RAG vector index
```

Full routing logic, Modelfile specs, and temperature rationale: [MODEL_ARCHITECTURE.md](MODEL_ARCHITECTURE.md)

---

## How Memory Works

### RAG — Semantic Memory

`RAGEngine` retrieves relevant code chunks for each request using AST-aware chunking and
importance-weighted cosine similarity.

**AST-aware chunking** — one function or class per chunk, never splitting mid-definition.
Preserves syntactic boundaries so retrieved chunks are always complete, runnable units.  
→ [snippets/ast_chunking.py](snippets/ast_chunking.py)

**Importance-weighted retrieval** — retrieval score blends semantic similarity (70%) with
chunk importance (30%). Importance factors: docstring presence, code length, reference
frequency in the codebase. Prevents low-quality utility functions from outranking
well-documented core logic.  
→ [snippets/weighted_similarity_search.py](snippets/weighted_similarity_search.py)

**Embeddings:** `nomic-embed-text` (local, 768-dim)  
**Index:** NumPy array persisted to `.vibe_index/rag_index.npy`  
**Similarity threshold:** 0.5

### CAG — Pattern Learning

`CAGMemory` stores accepted code changes as learned patterns and retrieves them on future
requests by intent and signature matching.

Every time the user accepts generated code, the system logs the signature, user intent,
and code delta with a confidence score. Future requests score stored patterns by intent
match (weight 2×) and signature match (weight 1×), returning the top-k most relevant
past solutions.

**Result:** The system improves at your specific codebase over time — without retraining.  
→ [snippets/cag_pattern_memory.py](snippets/cag_pattern_memory.py)

---

## Hallucination Gate

Generated code passes through five validation layers before it can be persisted to memory.
Code that fails is flagged for user review — never silently stored.

```
Layer 1: AST syntax check          → confidence 0.0 on failure (fatal)
Layer 2: Placeholder detection     → confidence -0.3 (pass/TODO/NotImplementedError)
Layer 3: Function preservation     → confidence -0.4 (missing functions from original)
Layer 4: Import consistency        → confidence -0.2 (missing or duplicate imports)
Layer 5: Infinite loop detection   → confidence -0.4 (while True without break)

Safe threshold: ≥ 0.6
```

→ [snippets/hallucination_detection.py](snippets/hallucination_detection.py)

---

## Three-Brain LLM System

Three purpose-trained model personas, each configured for its role:

| Brain | Model | Size | Temperature | Role |
|:------|:------|-----:|:-----------:|:-----|
| SOVEREIGN_CODER | qwen2.5-coder:7b | 7B | 0.2 | Code generation |
| FORENSIC_AUDITOR | mistral:7b-instruct | 7B | 0.0 | Validation (deterministic) |
| MAVERICK | llama3.2:3b | 3B | 0.3 | Intent routing |

Governance rules are enforced at two levels: system prompt injection (pre-generation) and
programmatic output validation (post-generation). Preambles, apologies, and markdown chatter
are blocked at the model level.

→ [snippets/multi_brain_governance.py](snippets/multi_brain_governance.py)  
→ [snippets/intent_routing.py](snippets/intent_routing.py)  
→ [MODEL_ARCHITECTURE.md](MODEL_ARCHITECTURE.md) — full Modelfile specs and temperature rationale

---

## The Vault (Persistent Memory)

All system memory lives in `.vibe_index/` and survives session termination:

```
.vibe_index/
├── rag_index.npy          ← embedding vectors (NumPy)
├── rag_metadata.json      ← chunk metadata (signature, file, importance)
├── learning_log.json      ← CAG patterns (last 100)
├── current_state.json     ← session state
├── feature_list.json      ← project feature tracking
└── vibe_memory.json       ← governance constitution
```

State is loaded clean on startup — only accepted, validated code is retained.
Non-accepted scratchpad work is filtered out to prevent hallucination pollution.

---

## Performance Benchmarks

**Hardware:** Intel Core i3-1115G4 (11th Gen), 36GB RAM, integrated GPU — ~$700 used laptop.

**MAVERICK (1B Organizer) — 20 sample requests:**

| Metric | Value |
|:-------|:------|
| Mean response | 7.76s |
| Median response | 5.76s |
| 95th percentile | 10.15s |
| Fastest | 3.92s |
| Slowest (cold start) | 18.31s |
| Excluding cold starts | 6.45s avg |

**SOVEREIGN_CODER (7B) — code generation:** 10–20s  
**FORENSIC_AUDITOR (7B) — validation:** 8–12s  
**Memory usage:** <2GB RAM during inference  
**Monthly cost:** $0

---

## Cost Comparison

100 requests/day, 30 days:

| Approach | Monthly Cost | Annual Cost |
|:---------|:------------:|:-----------:|
| GPT-4 API (single model) | $90.00 | $1,080.00 |
| This system (local, 3 models) | $0.00 | $0.00 |

Hardware break-even vs. cloud: **7.8 months**  
2-year net savings: **$1,460**

---

## Hardware Requirements

| Component | Minimum | Notes |
|:----------|:--------|:------|
| CPU | Intel i3 11th gen / Ryzen 3 | More cores = faster parallel inference |
| RAM | 16GB | Models load into RAM; 32GB+ recommended |
| Storage | 50GB SSD | Models ~7GB, Vault grows with usage |
| GPU | Not required | Integrated graphics sufficient |
| Network | Offline after model download | Zero runtime dependency |

**Total model storage:** ~7.2GB (one-time Ollama download)

---

## Setup

### 1. Install Ollama and pull base models
```bash
ollama pull qwen2.5-coder:7b-instruct-q4_K_M
ollama pull mistral:7b-instruct-v0.2-q4_0
ollama pull llama3.2:3b-instruct-q8_0
ollama pull nomic-embed-text
```

### 2. Create the three personas from Modelfiles
```bash
ollama create sovereign-coder -f modelfiles/sovereign-coder.Modelfile
ollama create forensic-auditor -f modelfiles/forensic-auditor.Modelfile
ollama create maverick -f modelfiles/maverick.Modelfile
```

### 3. Install dependencies
```bash
pip install flask requests numpy
```

### 4. Run
```bash
python my_coder.py
# UI available at http://localhost:5000
```

---

## Security & Privacy

All data stays local throughout the entire pipeline:

```
User Input → Flask (localhost:5000) → Ollama (localhost:11434) → Vault (filesystem)
                                                                  ↑
                                                        Never leaves local network
```

- No telemetry, no analytics, no vendor access
- Works fully offline after initial model download
- Constitutional governance rules enforced at system prompt and output validation layers

---

## Status

**Last updated:** January 2025  
**Deployment:** Local / on-premises only  
**License:** Proprietary

The full script is not open-source. Snippets and architecture documentation are provided
for evaluation purposes. Commercial licensing available on request.
