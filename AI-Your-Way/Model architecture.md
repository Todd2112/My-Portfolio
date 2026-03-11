# Model Architecture: Three-Brain Orchestration System

This document describes the multi-LLM architecture behind `my_coder.py` — three purpose-trained
model personas with different sampling configurations, orchestrated by intent-based routing.

---

## The Core Problem With Single-Model Systems

Routing every task through one generalized model wastes compute and reduces output quality:

| Task | Parameters Needed | GPT-4 Parameters Used | Waste Factor |
|:-----|:-----------------:|:---------------------:|:------------:|
| Intent classification | ~1B | 175B | 175× |
| Code validation | ~7B | 175B | 25× |
| Code generation | ~7B | 175B | 25× |

The solution: train specialized personas for each role, then route at the application layer.

---

## The Three Brains

### SOVEREIGN_CODER — Code Generation
```
Base model:  qwen2.5-coder:7b-instruct-q4_K_M
Temperature: 0.2   (low — consistent, repeatable output)
top_p:       0.9
num_ctx:     8192
```
**Why these parameters:** Code generation needs low creativity. Temperature 0.2 produces
consistent syntax and structure across repeated calls. Higher temperature introduces
unnecessary variation in variable names, spacing, and control flow.

**Role in system:** Handles all code generation, refactoring, and feature implementation.
Token limit: 4096 (full functions).

---

### FORENSIC_AUDITOR — Validation
```
Base model:  mistral:7b-instruct-v0.2-q4_0
Temperature: 0.0   (fully deterministic — same input always produces same verdict)
top_p:       0.1   (near-greedy decoding)
num_ctx:     8192
```
**Why these parameters:** A validator must be deterministic. Temperature 0.0 with top_p 0.1
forces greedy token selection — the model always picks the highest-probability next token.
Any temperature above 0 introduces stochastic verdicts, which is unacceptable for a
pass/fail gate.

**Role in system:** Post-generation code review. Returns only `PASS` or `FAIL: <issue>`.
Token limit: 1024 (verdicts, not essays).

---

### MAVERICK — Intent Classification & Routing
```
Base model:  llama3.2:3b-instruct-q8_0
Temperature: 0.3   (slight flexibility for ambiguous input)
num_ctx:     8192
```
**Why these parameters:** Intent classification handles ambiguous natural language.
Temperature 0.3 allows slight flexibility when user phrasing is non-standard, while
staying close enough to deterministic for clear cases. Higher temperature would
produce inconsistent routing decisions.

**Role in system:** Classifies user intent into one of six categories
(`modify-target`, `retrieve`, `review`, `fix`, `explain`, `general`).
Token limit: 512 (single keyword output).

---

## Routing Architecture

```
User Input
    ↓
[Keyword Bypass Layer]  ← deterministic, no LLM call
    • AUDIT_KEYWORDS → "review" path
    • MODIFY_KEYWORDS → "modify-target" path
    ↓ (ambiguous input only)
[MAVERICK — 1B Organizer]  ← LLM classification fallback
    ↓
┌────────────────┬─────────────┬──────────────┐
│ SOVEREIGN_CODER│   Retrieve  │   Review     │
│ Code generation│  RAG search │  FORENSIC_   │
│ (7B, temp 0.2) │             │  AUDITOR     │
│                │             │  (7B, temp 0)│
└────────────────┴─────────────┴──────────────┘
    ↓
[Hallucination Gate]  ← confidence scoring, AST validation
    ↓ (if confidence ≥ 0.6)
[Vault Persistence]  ← CAG pattern log + RAG vector index
```

---

## Why This Works on Consumer Hardware

60–70% of requests are routed to the 1B MAVERICK model for classification.
Only generation and validation calls hit the 7B models.
The 3B model is used sparingly for routing edge cases.

**Result:** Median response time 5.76s on an Intel i3 with integrated graphics and 36GB RAM.
No GPU required.

---

## Modelfile Location

Modelfiles for all three personas are in the `modelfiles/` directory:
- `modelfiles/sovereign-coder.Modelfile`
- `modelfiles/forensic-auditor.Modelfile`
- `modelfiles/maverick.Modelfile`

Deploy with: `ollama create <name> -f modelfiles/<name>.Modelfile`
