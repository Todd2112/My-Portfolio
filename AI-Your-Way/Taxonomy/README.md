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

![Matching results](AI-Your-Way/Taxonomy/ecommerce_screenshot2.png)

**Then I took it further.** The cleaned output exports as CSV or JSON, feeds a local vector index, and gets checked in a Data Readiness Console that audits the results and tests live retrieval.

The first run broke, and I'm leaving that in:

- My "quality gate" was only a label, so unreviewed rows were still searchable
- Category and status text was baked into the embeddings and skewed the scores
- 3 of 4 test queries returned "no answer," and one answer was invented outright

After fixing the gate, the embeddings, and the test questions: **5 of 5 correct, grounded answers.**

![Audit](AI-Your-Way/Taxonomy/ecommerce_screenshot3.png)

**Still not done:** my tests used exact product names, so I haven't proven paraphrase recall yet. The backlog of rows waiting on review is the real job. It's retrieval-ready for the accepted slice, not the whole dataset.

Full write-up, warts and all: **[link to article]**

*Data: "Online Retail" dataset (Dr. Daqing Chen, London South Bank University, via UCI/Kaggle). Used for testing only.*

---

## Demo 1: No Guessing, Even When It Looks Bad

A real legislative text dataset (`R45348.2.pdf`), loaded with only **one** category defined: `Federal Framework Legislation`.

![Baseline run](AI-Your-Way/Taxonomy/screen_shot1.png)

The tool pulled the text out of the PDF, scanned 5 rows, and surfaced the most common words in the actual corpus. No manual tagging.

![Word Ranking](AI-Your-Way/Taxonomy/screen_shot2.png)

**Result: 0 auto-accepted, 1 needs review, 4 no match.**

That's correct. One category can't cover most of that content, so the tool refused to force a match. A tool that always gives you an answer isn't helping you. It's hiding the problem.

![Result](AI-Your-Way/Taxonomy/screen_shot3.png)

---

## Demo 2: Fix the Taxonomy, Watch It Improve

I added a second category (`Executive and Administrative Directives`, with alternate labels: OMB, Circular, Executive Order, Guidance) and re-ran the identical five rows.

![Add Category](AI-Your-Way/Taxonomy/2nd_run_screenshot1.png)

**0 of 5 jumped to 2 of 5 auto-accepted.** No code changes, just a better-defined taxonomy.

![Result](AI-Your-Way/Taxonomy/2nd_run_screenshot2.png)

![Result II](AI-Your-Way/Taxonomy/2nd_run_screenshot3.png)

---

## Demo 3: Teach It Once, It Remembers

For the two rows still unresolved, I picked the right category from a dropdown and clicked **Teach**.

This isn't a one-off fix. The correction is written permanently into the category, so the same or similar term matches automatically from now on. That's the loop that shrinks the review backlog.

![Result I](AI-Your-Way/Taxonomy/3rd_run_screenshot1.png)

![Result II](AI-Your-Way/Taxonomy/3rd_run_screenshot2.png)

![Result III](AI-Your-Way/Taxonomy/3rd_run_screenshot3.png)

Both corrected rows now show `human taught` at 100% confidence in the permanent history. Every match and every correction is on record. Nothing silent, nothing untracked.

![Result](AI-Your-Way/Taxonomy/3rd_run_screenshot4.png)

---

## Demo 4: Resumes, a Completely Different Domain

Same engine, different world. An actual resume (`todd_lipscomb_resume_v5.pdf`), extracted straight from the PDF with no retyping, matched against three job-fit categories I built for this run.

![Result](AI-Your-Way/Taxonomy/resume_screenshot1.png)

![Result](AI-Your-Way/Taxonomy/resume_screenshot2.png)

Real-world files are messy. This one had leftover citation markers like `[cite: 2]` from another tool, and the scan handled them without breaking.

![Result](AI-Your-Way/Taxonomy/resume_screenshot3.png)

**Result: 5 of 5 lines auto-accepted at 90% confidence**, sorted into Sovereign AI Systems Architect, Senior Backend & Tooling Engineer, and Regulatory Compliance & Transaction Operations. Zero manual review once the categories were defined properly.

![Result](AI-Your-Way/Taxonomy/resume_screenshot4.png)

---

## What This Proves

- **Domain-agnostic.** Legislative text, resumes, product catalogs, accounting data. Same engine, zero code changes.
- **Never silently guesses.** Confidence-gated at every step. Low-confidence matches are flagged, not forced.
- **Real PDF handling.** Server-side extraction that works on regulatory documents and resumes alike.
- **Actually learns.** Corrections go into the taxonomy itself, permanently, not into a log nobody reads.
- **Fully auditable.** Every match and every correction is timestamped and retrievable.
- **Scales locally.** 540K rows on a single consumer machine, CPU only, no cloud.
- **Retrieval-ready output.** Cleaned, confidence-gated data exports straight into a local vector index, with only reviewed rows eligible for AI retrieval.

---

## Who This Is For

Teams whose data can't leave their network, especially in regulated work like legal, healthcare, and real estate compliance. If your data needs to be clean before AI touches it, and you need to prove how it got clean, that's the job.

---
