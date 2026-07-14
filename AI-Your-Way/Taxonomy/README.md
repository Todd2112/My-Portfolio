# Taxonomy Cleanup Tool — Portfolio Demo

**Local-only, confidence-gated data cleaning and categorization.** Built for taxonomy, metadata standardization, and messy-data classification work — job titles, resumes, regulatory text, product catalogs, or any text-based dataset a client needs structured.

---

## Demo 1: Baseline Run — Honest Confidence Gating, No Guessing

A real regulatory/legislative text dataset (`R45348.2.pdf`), loaded with only one category defined (`Federal Framework Legislation`). This shows the system's core behavior: it refuses to force a match when confidence is low, rather than guessing.

<insert screen_shot1.png here>

Loaded the PDF, extracted and scanned 5 rows, surfaced the most common words in the actual corpus (no manual tagging).

<insert screen_shot2.png here>

Result: 0 auto-accepted, 1 needs review, 4 no match — because only one category existed and it genuinely didn't cover most of the content. This is correct, not a failure.

<insert screen_shot3.png here>

---

## Demo 2: Adding a Category — Watching the System Actually Improve

Added a second category (`Executive and Administrative Directives`, alt labels: OMB, Circular, Executive Order, Guidance) to the same category set. Re-ran the identical five rows.

<insert 2nd_run_screenshot1.png here>

Result jumped from 0/5 to 2/5 auto-accepted immediately — no code changes, just a better-defined taxonomy.

<insert 2nd_run_screenshot2.png here>

<insert 2nd_run_screenshot3.png here>

---

## Demo 3: Teach-the-System — Closing the Loop

For the two remaining unresolved rows, used the built-in correction feature: picked the right category from a dropdown and clicked Teach. This isn't a one-off fix — it's written permanently into that category's data, so the same or similar term matches automatically from now on.

<insert 3rd_run_screenshot1.png here>

<insert 3rd_run_screenshot2.png here>

<insert 3rd_run_screenshot3.png here>

Both corrected rows now show `human taught` at 100% confidence in the permanent audit history — a full record of every match and every human correction, nothing silent or untracked.

<insert 3rd_run_screenshot4.png here>

---

## Demo 4: Resume / Job-Fit Matching — Real PDF, Real Results

A completely different domain and dataset: an actual resume (`todd_lipscomb_resume_v5.pdf`), extracted directly from PDF (no manual retyping), matched against three custom job-fit categories built specifically for this run.

<insert resume_screenshot1.png here>

<insert resume_screenshot2.png here>

Corpus scan on the extracted resume text — note it handles messy real-world artifacts (inline citation markers like `[cite: 2]` left over from another tool) without breaking.

<insert resume_screenshot3.png here>

Final result: 5 of 5 lines auto-accepted at 90% confidence, correctly sorted into role categories (Sovereign AI Systems Architect, Senior Backend & Tooling Engineer, Regulatory Compliance & Transaction Operations) — zero manual review needed once the categories were properly defined.

<insert resume_screenshot4.png here>

---

## What This Demonstrates

- **Domain-agnostic** — same engine, zero code changes, across legislative text, resumes, and (elsewhere) product catalogs and accounting data.
- **Never silently guesses** — confidence-gated at every step; low-confidence matches are flagged, not forced.
- **Real PDF handling** — server-side extraction, not a client-side trick, works on scanned regulatory documents and resumes alike.
- **Actually learns** — human corrections are written into the taxonomy itself, permanently, not just logged and forgotten.
- **Fully auditable** — every match and every correction is timestamped and retrievable.
