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

