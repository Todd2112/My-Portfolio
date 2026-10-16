# Taxonomy Cleanup Tool

**Everyone wants AI. Almost nobody wants to clean the data first.**

That's the gap this tool lives in. It takes messy text (product names, job titles, resumes, regulatory documents, expense lines) and sorts it into categories you define. It runs **100% local**: no cloud, no API keys, no data leaving your machine.

The rule it never breaks: **if it isn't sure, it says so.** High confidence gets accepted. Anything shaky gets flagged for a human. It never guesses.

Tool, not toy.

---

## The Short Version

| What | How |
|---|---|
| **Privacy** | Fully local. Your data stays on your hardware. |
| **Honesty** | Confidence-gated. Low-confidence rows are flagged, never forced. |
| **Learning** | Human corrections are saved permanently and reused. |
| **Audit trail** | Every match and every correction is logged and retrievable. |
| **Any domain** | Same engine, zero code changes, across very different datasets. |

---

## Demo 5: The Stress Test: 540K Real Transactions

*This is the big one, so it goes first.*

I ran the public "Online Retail" dataset from Kaggle through the tool: 541,909 raw transactions from a UK gift retailer. About 4,200 unique products, repeated roughly 129 times each. Six starter categories. Fully local, CPU only, one consumer machine.

![Load the data](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/Taxonomy/screen.png)

**The honest numbers:**

- 540,455 rows processed in 2,703 batches
- **26,092 auto-accepted (4.8%)**
- **322,876 needs review (59.7%)**
- **191,487 no match (35.4%)**

After a full automated pass, 95% of the data still needs a person. That's not a bug. My starter taxonomy was too thin, and the audit made it obvious. Better to know than to hide it.

![Matching results](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/Taxonomy/screen4.png)

**Then I took it further.** The cleaned output exports as CSV or JSON, feeds a local vector index, and gets checked in a Data Readiness Console that audits the results and tests live retrieval.

The first run broke, and I'm leaving that in:

- My "quality gate" was only a label, so unreviewed rows were still searchable
- Category and status text was baked into the embeddings and skewed the scores
- 3 of 4 test queries returned "no answer," and one answer was invented outright

After fixing the gate, the embeddings, and the test questions: **5 of 5 correct, grounded answers.**

![Audit](https://github.com/Todd2112/My-Portfolio/blob/master/AI-Your-Way/Taxonomy/screen11.png)

**Still not done:** my tests used exact product names, so I haven't proven paraphrase recall yet. The backlog of rows waiting on review is the real job. It's retrieval-ready for the accepted slice, not the whole dataset.

Full write-up, warts and all: **(https://www.linkedin.com/pulse/everyone-wants-ai-almost-nobody-clean-data-first-todd-lipscomb-utivc)**

*Data: "Online Retail" dataset (Dr. Daqing Chen, London South Bank University, via UCI/Kaggle). Used for testing only.*

---

## Under the Hood

No magic here. Deterministic code first, LLM last. The real snippets, trimmed:

### 1. The confidence gate (`pipeline.py`)

Two thresholds decide everything. Below the floor, it's `no_match`. Above the ceiling, it's accepted. Everything in between goes to a human.

```python
AUTO_ACCEPT_THRESHOLD = 0.85
REVIEW_THRESHOLD = 0.60

if not top or top["confidence"] < REVIEW_THRESHOLD:
    status = "no_match"
    ...
elif top["confidence"] >= AUTO_ACCEPT_THRESHOLD:
    status = "auto_accepted"
else:
    status = "needs_review"
```

Every row ends up as one of five statuses: `auto_accepted`, `needs_review`, `no_match`, `llm_matched`, or `human_taught`.

### 2. Teach once, remembered forever (`pipeline.py`)

When a person fixes a row, the correction is stored at 100% confidence with its own status. It's never overwritten, and it shows up in the audit history.

```python
(payload.term, payload.concept_id, row["pref_label"], 1.0, "human_taught")
```

### 3. Embed the text, not the labels (`merge_vector.py`)

My first run embedded `CATEGORY | STATUS | text` together, which skewed the similarity scores. Now only the raw text is embedded. Category and status stay as metadata.

```python
# Embed the raw text only; category/status stay as metadata
# so they do not skew similarity scores.
embed_text = text_chunk
```

### 4. 540K rows, ~4,200 embeds (`merge_vector.py`)

Identical texts are embedded once and reused. That's why a half-million-row compile takes about a minute on CPU.

```python
for r in records:
    t = r["embed_text"]
    if t not in text_to_unique_idx:
        text_to_unique_idx[t] = len(unique_texts)
        unique_texts.append(t)
    record_to_unique_idx.append(text_to_unique_idx[t])
```

### 5. The review gate at query time (`kb_console.py`)

The gate isn't a label. Rows that haven't cleared review are filtered out before the LLM ever sees them. This was the fix from the first run.

```python
USABLE_STATUSES = {"auto_accepted", "human_taught", "llm_matched"}

for score, idx in zip(scores[0], ids[0]):
    rec = records[idx]
    if rec.get("status") not in USABLE_STATUSES:
        continue
```

### The stack

- **Python**, with FastAPI for the local interface
- **Ollama** for local embeddings (`bge-small`, quantized, CPU only)
- **FAISS** (`IndexFlatIP`) for vector search
- **SQLite** for the taxonomy and audit history
- **No cloud. No API keys. No GPU.**
