<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Todd M. Lipscomb — Reliability Infrastructure for Inference at the Edge</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;1,8..60,300;1,8..60,400&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>

/* ── RESET & ROOT ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --ink:        #0a0e17;
  --paper:      #070b12;
  --surface:    #0d1420;
  --rule:       #1a2235;
  --rule-hi:    #243048;
  --text:       #c8d4e8;
  --text-dim:   #5a6a85;
  --text-muted: #3a4a60;
  --accent:     #4a9eff;
  --accent-dim: #1a3a6a;
  --accent-lo:  #0d1f3a;
  --green:      #2dd4a0;
  --green-dim:  #0a3328;
  --amber:      #f0a030;
  --red:        #e05555;
  --serif:      'Source Serif 4', Georgia, serif;
  --mono:       'JetBrains Mono', 'Cascadia Code', monospace;
  --col:        680px;
  --wide:       960px;
}

html { scroll-behavior: smooth; }

body {
  font-family: var(--serif);
  background: var(--paper);
  color: var(--text);
  line-height: 1.75;
  font-size: 17px;
  font-weight: 300;
  overflow-x: hidden;
}

/* ── GRAIN OVERLAY ───────────────────────────────────────── */
body::after {
  content: '';
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
  opacity: 0.6;
}

/* ── LAYOUT ──────────────────────────────────────────────── */
.page { max-width: var(--wide); margin: 0 auto; padding: 0 40px 120px; }

/* ── MASTHEAD ────────────────────────────────────────────── */
.masthead {
  border-bottom: 1px solid var(--rule-hi);
  padding: 48px 0 40px;
  margin-bottom: 0;
  position: relative;
}
.masthead-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}
.doc-series {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--accent);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-bottom: 16px;
}
.doc-series::before { content: '// '; color: var(--text-muted); }

.author-name {
  font-family: var(--serif);
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 600;
  color: #e8f0ff;
  letter-spacing: -0.02em;
  line-height: 1.1;
  margin-bottom: 8px;
}
.author-title {
  font-family: var(--mono);
  font-size: 0.75rem;
  color: var(--text-dim);
  letter-spacing: 0.08em;
  line-height: 1.8;
}
.author-title span { color: var(--accent); }

.masthead-meta {
  text-align: right;
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  line-height: 2;
}
.masthead-meta a { color: var(--accent); text-decoration: none; }
.masthead-meta a:hover { color: var(--text); }

/* status indicator */
.status-line {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-top: 20px;
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  letter-spacing: 0.1em;
}
.status-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 8px var(--green);
  animation: pulse 2.5s ease infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.status-line .sep { color: var(--rule-hi); }

/* ── ABSTRACT ────────────────────────────────────────────── */
.abstract {
  border-left: 2px solid var(--accent-dim);
  margin: 52px 0;
  padding: 32px 40px;
  background: var(--accent-lo);
  position: relative;
}
.abstract::before {
  content: 'ABSTRACT';
  position: absolute;
  top: -10px; left: 40px;
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  color: var(--accent);
  background: var(--accent-lo);
  padding: 0 8px;
}
.abstract p {
  font-size: 0.975rem;
  line-height: 1.85;
  color: #a0b8d8;
  font-style: italic;
}
.abstract p + p { margin-top: 16px; }

/* ── SECTION ─────────────────────────────────────────────── */
.section { margin-top: 64px; }

.section-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 16px;
  margin-bottom: 36px;
}
.section-num {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--accent);
  letter-spacing: 0.1em;
}
.section-rule { height: 1px; background: var(--rule); }
.section-title {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--text-dim);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  white-space: nowrap;
}

/* ── PROSE ───────────────────────────────────────────────── */
.prose { max-width: var(--col); }
.prose p { margin-bottom: 20px; font-size: 0.975rem; color: var(--text); }
.prose p:last-child { margin-bottom: 0; }
.prose strong { color: #d0e0f8; font-weight: 600; }
.prose em { color: var(--accent); font-style: normal; font-family: var(--mono); font-size: 0.85em; }

/* ── THESIS GRID ─────────────────────────────────────────── */
.thesis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--rule);
  border: 1px solid var(--rule);
  margin-top: 32px;
}
.thesis-card {
  background: var(--surface);
  padding: 28px;
  transition: background 0.2s;
}
.thesis-card:hover { background: #111926; }
.thesis-problem {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--red);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.thesis-solution {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--green);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.thesis-card h3 {
  font-family: var(--serif);
  font-size: 0.95rem;
  font-weight: 600;
  color: #d8e8ff;
  margin-bottom: 10px;
  line-height: 1.3;
}
.thesis-card p {
  font-size: 0.82rem;
  color: var(--text-dim);
  line-height: 1.65;
}
.thesis-card code {
  font-family: var(--mono);
  font-size: 0.78rem;
  color: var(--accent);
  background: var(--accent-lo);
  padding: 1px 5px;
  border-radius: 2px;
}

/* ── PROJECT ENTRIES ─────────────────────────────────────── */
.project { margin-bottom: 56px; padding-bottom: 56px; border-bottom: 1px solid var(--rule); }
.project:last-child { border-bottom: none; }

.project-header {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}
.project-id {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
  letter-spacing: 0.12em;
  flex-shrink: 0;
}
.project-name {
  font-family: var(--serif);
  font-size: 1.25rem;
  font-weight: 600;
  color: #dceeff;
  letter-spacing: -0.01em;
}
.project-subtitle {
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--accent);
  margin-bottom: 20px;
  letter-spacing: 0.06em;
}

.project-body {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 40px;
  align-items: start;
}
.project-desc p {
  font-size: 0.925rem;
  color: var(--text);
  line-height: 1.8;
  margin-bottom: 16px;
}
.project-desc p:last-child { margin-bottom: 0; }
.project-desc strong { color: #d0e0f8; font-weight: 600; }

.project-spec {
  font-family: var(--mono);
  font-size: 0.7rem;
  border: 1px solid var(--rule-hi);
  background: var(--surface);
}
.spec-row {
  display: grid;
  grid-template-columns: 90px 1fr;
  border-bottom: 1px solid var(--rule);
}
.spec-row:last-child { border-bottom: none; }
.spec-key {
  padding: 8px 10px;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.6rem;
  border-right: 1px solid var(--rule);
  display: flex;
  align-items: flex-start;
  padding-top: 10px;
}
.spec-val {
  padding: 8px 10px;
  color: var(--text-dim);
  line-height: 1.6;
  font-size: 0.68rem;
}
.spec-val .hi { color: var(--accent); }
.spec-val .ok { color: var(--green); }

/* ── PUBLICATION ─────────────────────────────────────────── */
.publication {
  border: 1px solid var(--rule-hi);
  padding: 28px 32px;
  background: var(--surface);
  margin-top: 20px;
}
.pub-label {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--amber);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.pub-title {
  font-family: var(--serif);
  font-size: 1.05rem;
  font-weight: 600;
  color: #dceeff;
  line-height: 1.4;
  margin-bottom: 8px;
}
.pub-meta {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-bottom: 16px;
  letter-spacing: 0.06em;
}
.pub-abstract {
  font-size: 0.875rem;
  color: var(--text-dim);
  line-height: 1.75;
  font-style: italic;
  border-left: 2px solid var(--rule-hi);
  padding-left: 16px;
}

/* ── CREDENTIALS TABLE ───────────────────────────────────── */
.cred-table { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 0.7rem; }
.cred-table thead tr { border-bottom: 1px solid var(--rule-hi); }
.cred-table th {
  padding: 8px 12px;
  text-align: left;
  color: var(--text-muted);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 0.6rem;
  font-weight: 400;
}
.cred-table td { padding: 10px 12px; border-bottom: 1px solid var(--rule); color: var(--text-dim); vertical-align: top; }
.cred-table tr:last-child td { border-bottom: none; }
.cred-table tr:hover td { background: var(--surface); }
.cred-table .issuer { color: var(--accent); font-weight: 500; }
.cred-table .cert-name { color: var(--text); }
.cred-table .date { color: var(--text-muted); white-space: nowrap; }
.cred-table a { color: var(--accent); text-decoration: none; opacity: 0.7; }
.cred-table a:hover { opacity: 1; }

/* ── STACK MATRIX ────────────────────────────────────────── */
.stack-matrix {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--rule);
  border: 1px solid var(--rule);
  margin-top: 20px;
}
.stack-col { background: var(--surface); padding: 20px; }
.stack-col-label {
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--rule);
}
.stack-item {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--text-dim);
  padding: 4px 0;
  border-bottom: 1px solid var(--rule);
  transition: color 0.15s;
}
.stack-item:last-child { border-bottom: none; }
.stack-item:hover { color: var(--accent); }
.stack-item .dot { color: var(--accent); margin-right: 6px; }

/* ── POSITION STATEMENT ──────────────────────────────────── */
.position {
  margin-top: 52px;
  padding: 40px;
  border: 1px solid var(--rule-hi);
  background: var(--surface);
  position: relative;
}
.position::before {
  content: '§ POSITION';
  font-family: var(--mono);
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  color: var(--text-muted);
  display: block;
  margin-bottom: 20px;
}
.position p {
  font-size: 1rem;
  line-height: 1.85;
  color: var(--text);
  max-width: var(--col);
}
.position p + p { margin-top: 18px; }
.position strong { color: #e0ecff; font-weight: 600; }

/* ── CONTACT ─────────────────────────────────────────────── */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--rule);
  border: 1px solid var(--rule);
  margin-top: 20px;
}
.contact-item {
  background: var(--surface);
  padding: 16px 20px;
  font-family: var(--mono);
}
.contact-label {
  font-size: 0.55rem;
  color: var(--text-muted);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.contact-value { font-size: 0.7rem; color: var(--accent); }
.contact-value a { color: inherit; text-decoration: none; }
.contact-value a:hover { color: var(--text); }

/* ── FOOTER ──────────────────────────────────────────────── */
.footer {
  margin-top: 80px;
  padding: 24px 0;
  border-top: 1px solid var(--rule);
  display: flex;
  justify-content: space-between;
  font-family: var(--mono);
  font-size: 0.6rem;
  color: var(--text-muted);
  letter-spacing: 0.1em;
}

/* ── FADE IN ─────────────────────────────────────────────── */
.fade { opacity: 0; transform: translateY(12px); animation: fadeUp 0.6s ease forwards; }
@keyframes fadeUp { to { opacity:1; transform:translateY(0); } }
.d1{animation-delay:.05s} .d2{animation-delay:.15s} .d3{animation-delay:.25s}
.d4{animation-delay:.35s} .d5{animation-delay:.45s} .d6{animation-delay:.55s}

/* ── RESPONSIVE ──────────────────────────────────────────── */
@media (max-width: 720px) {
  .page { padding: 0 20px 80px; }
  .thesis-grid { grid-template-columns: 1fr; }
  .project-body { grid-template-columns: 1fr; }
  .stack-matrix { grid-template-columns: 1fr; }
  .contact-grid { grid-template-columns: 1fr 1fr; }
  .masthead-top { flex-direction: column; gap: 20px; }
  .masthead-meta { text-align: left; }
}

</style>
</head>
<body>
<div class="page">

  <!-- ── MASTHEAD ──────────────────────────────────────── -->
  <header class="masthead fade d1">
    <div class="masthead-top">
      <div>
        <div class="doc-series">Technical Dossier · TML Investments LLC · Revision 2026.1</div>
        <div class="author-name">Todd M. Lipscomb</div>
        <div class="author-title">
          Reliability Infrastructure for Inference at the Edge<br>
          <span>Local LLM</span> · <span>Multi-Agent Architecture</span> · <span>Sovereign AI Systems</span>
        </div>
      </div>
      <div class="masthead-meta">
        <div>Trenton, MI · Remote</div>
        <div><a href="mailto:realtodd@yahoo.com">realtodd@yahoo.com</a></div>
        <div><a href="https://github.com/Todd2112" target="_blank">github.com/Todd2112</a></div>
        <div><a href="https://linkedin.com/in/todd-lipscomb-670458290" target="_blank">linkedin.com/in/todd-lipscomb-670458290</a></div>
        <div><a href="https://upwork.com" target="_blank">upwork.com · TML Investments LLC</a></div>
      </div>
    </div>
    <div class="status-line">
      <div class="status-dot"></div>
      <span>SYSTEMS ACTIVE</span>
      <span class="sep">·</span>
      <span>ALL INFERENCE LOCAL</span>
      <span class="sep">·</span>
      <span>ZERO EXTERNAL API DEPENDENCY</span>
      <span class="sep">·</span>
      <span id="ts"></span>
    </div>
  </header>

  <!-- ── ABSTRACT ──────────────────────────────────────── -->
  <div class="abstract fade d2">
    <p>This document presents the research contributions, system architectures, and engineering methodology of Todd M. Lipscomb, operating under TML Investments LLC. The body of work herein constitutes a coherent research agenda directed at a single problem: making small, locally-deployed language models reliable enough for high-stakes production use in regulated and security-sensitive environments.</p>
    <p>The failure modes addressed — context drift, hallucination, stateless inference, retrieval imprecision, and model convergence instability — are not incidental. They are structural properties of how commercial LLM systems are designed and monetized. The engineering position taken throughout this work is that these failures are solvable at the architectural level, without cloud dependency, without large-parameter models, and without recurring infrastructure cost. The systems documented here constitute proof of that position.</p>
  </div>

  <!-- ── SECTION 1: RESEARCH POSITION ──────────────────── -->
  <section class="section fade d3">
    <div class="section-header">
      <span class="section-num">§ 01</span>
      <div class="section-rule"></div>
      <span class="section-title">Research Position &amp; Technical Thesis</span>
    </div>

    <div class="prose">
      <p>The dominant discourse in applied AI engineering is preoccupied with scale — larger parameter counts, higher-bandwidth inference APIs, and increasingly opaque foundation models. This trajectory is commercially motivated. Systems that forget context require repeated queries. Stateless inference necessitates subscription revenue. Hallucination, left unaddressed, creates dependency on human correction loops that further entrench vendor relationships.</p>
      <p>The work presented here proceeds from the opposite premise: that <strong>inference reliability is an engineering problem, not a hardware problem.</strong> The relevant variables are architectural — how agents are scoped, how memory is persisted, how retrieval is verified, how output is validated before it propagates downstream.</p>
      <p>Six specific failure modes are targeted across this body of work:</p>
    </div>

    <div class="thesis-grid">
      <div class="thesis-card">
        <div class="thesis-problem">Failure Mode</div>
        <h3>Context Drift &amp; Lost-in-the-Middle</h3>
        <p>LLMs with long context windows systematically underweight tokens in the middle of the context. Degradation compounds with session length, producing contradictory or hallucinated outputs late in complex tasks.</p>
        <div style="margin-top:12px;"><div class="thesis-solution">Architectural Response</div>
        <p>Multi-agent specialization. Each model handles a single, bounded cognitive task. No agent accumulates context beyond its defined scope. Implemented across <code>my_coder.py</code>, <code>legal_engine</code>, <code>audit_engine</code>.</p></div>
      </div>
      <div class="thesis-card">
        <div class="thesis-problem">Failure Mode</div>
        <h3>Hallucination &amp; Output Integrity</h3>
        <p>Generative models produce syntactically valid but semantically incorrect output with high confidence. In code generation, legal analysis, and financial auditing, this is not a nuisance — it is a liability.</p>
        <div style="margin-top:12px;"><div class="thesis-solution">Architectural Response</div>
        <p>Five-layer AST validation, zero-chatter sanitization, confidence scoring, and adversarial hardening. The <code>my_cli.py</code> Red Team Auditor subjects outputs to CVE-cross-referenced security analysis before persistence.</p></div>
      </div>
      <div class="thesis-card">
        <div class="thesis-problem">Failure Mode</div>
        <h3>Stateless Inference &amp; Memory Loss</h3>
        <p>Commercial LLM sessions are ephemeral by design. Session termination destroys accumulated context. Persistent domain knowledge requires re-injection on every call, generating token cost and retrieval noise.</p>
        <div style="margin-top:12px;"><div class="thesis-solution">Architectural Response</div>
        <p>FAISS vector stores with versioned indices, CAG pattern learning with Reflex Buffer, and persistent session vaults. Memory is stored deterministically, not reconstructed probabilistically.</p></div>
      </div>
      <div class="thesis-card">
        <div class="thesis-problem">Failure Mode</div>
        <h3>Retrieval Imprecision</h3>
        <p>Naive RAG implementations retrieve by approximate similarity without verification. Outlier documents, embedding drift, and cross-domain contamination degrade retrieval precision in multi-document corpora.</p>
        <div style="margin-top:12px;"><div class="thesis-solution">Architectural Response</div>
        <p>Deterministic outlier detection via mean/std distance thresholding, semantic reranking before context injection, and cosine drift scoring for identity verification in generative pipelines.</p></div>
      </div>
      <div class="thesis-card">
        <div class="thesis-problem">Failure Mode</div>
        <h3>Model Convergence Instability</h3>
        <p>Fixed-epoch fine-tuning regimes exit training at arbitrary points — either underfitting domain-specific patterns or overfitting to training artifacts. Standard loss curves provide insufficient signal for complex identity tasks.</p>
        <div style="margin-top:12px;"><div class="thesis-solution">Architectural Response</div>
        <p>Four-phase adaptive LoRA training with Welford online statistical tracking, sliding-window slope analysis, and p-value plateau detection. Training exits on verified convergence, not epoch count.</p></div>
      </div>
      <div class="thesis-card">
        <div class="thesis-problem">Failure Mode</div>
        <h3>Data Sovereignty Failure</h3>
        <p>Every API call is a trust decision, a cost, a latency dependency, and a data exposure event. For legal, financial, and security-sensitive workloads, cloud-based inference is not a tradeoff — it is a structural liability.</p>
        <div style="margin-top:12px;"><div class="thesis-solution">Architectural Response</div>
        <p>Air-gap capable inference across all systems. All models run locally via Ollama. No telemetry, no external calls, no vendor dependency post-deployment. Verifiably offline via OS-level firewall controls.</p></div>
      </div>
    </div>
  </section>

  <!-- ── SECTION 2: SYSTEMS ─────────────────────────────── -->
  <section class="section fade d4">
    <div class="section-header">
      <span class="section-num">§ 02</span>
      <div class="section-rule"></div>
      <span class="section-title">System Architectures &amp; Implementations</span>
    </div>

    <!-- PROJECT 1 -->
    <div class="project">
      <div class="project-header">
        <span class="project-id">SYS-001</span>
        <span class="project-name">Sovereign Legal Discovery Engine</span>
      </div>
      <div class="project-subtitle">Dual-Agent Legal Document Analysis · Air-Gap Capable · FastAPI + Ollama</div>
      <div class="project-body">
        <div class="project-desc">
          <p>Designed for the specific failure mode of cloud-based legal AI: attorney-client privilege cannot survive transmission to a third-party inference API. The engine runs entirely on-premises, processing privileged documents through a dual-agent pipeline without any external network dependency.</p>
          <p>The <strong>Auditor agent</strong> (LLaMA 3.2 3B-instruct-q8) performs clinical extraction — holdings, precedents, contract clauses, and risk factors — into a structured JSON ledger. The <strong>Narrator agent</strong> (LLaMA 3.2 1B-instruct-q4) generates the human-readable audit trail with mission-keyword highlighting. Agent boundary enforcement prevents context bleed between extraction and narration tasks.</p>
          <p>A three-stage ingestion pipeline handles document quality variance: structural parsing via pdfplumber, automatic OCR pivot via Tesseract when text density falls below threshold, and a quality gate that halts processing rather than propagating low-confidence extraction. The Logic Store allows operators to define custom extraction schemas and column structures per case type — SCOTUS audit, deposition summary, contract review, entity extraction — without modifying system code.</p>
        </div>
        <div class="project-spec">
          <div class="spec-row"><span class="spec-key">Status</span><span class="spec-val"><span class="ok">Production</span></span></div>
          <div class="spec-row"><span class="spec-key">Agents</span><span class="spec-val">Auditor (3B) · Narrator (1B)</span></div>
          <div class="spec-row"><span class="spec-key">Ingestion</span><span class="spec-val">pdfplumber → PyPDF2 → Tesseract OCR</span></div>
          <div class="spec-row"><span class="spec-key">Backend</span><span class="spec-val">FastAPI · Async Python</span></div>
          <div class="spec-row"><span class="spec-key">Output</span><span class="spec-val">Structured JSON ledger · CSV export</span></div>
          <div class="spec-row"><span class="spec-key">Privacy</span><span class="spec-val"><span class="hi">Air-gap capable</span></span></div>
          <div class="spec-row"><span class="spec-key">Hardware</span><span class="spec-val">16GB RAM laptop · No GPU required</span></div>
        </div>
      </div>
    </div>

    <!-- PROJECT 2 -->
    <div class="project">
      <div class="project-header">
        <span class="project-id">SYS-002</span>
        <span class="project-name">Multi-Agent RAG Backend</span>
      </div>
      <div class="project-subtitle">Triple-LLM Agent System · FAISS Multi-KB Retrieval · Semantic Reranking</div>
      <div class="project-body">
        <div class="project-desc">
          <p>A production retrieval-augmented generation system designed for multi-knowledge-base environments. The architecture routes queries through three specialized agents — <strong>Initializer</strong> (query decomposition and intent classification), <strong>Orchestrator</strong> (retrieval coordination and context assembly), and <strong>Reasoner</strong> (final synthesis and answer generation) — each operating on bounded context to prevent cross-contamination.</p>
          <p>Cross-KB retrieval queries multiple FAISS indices simultaneously, with per-model semantic reranking applied before context injection into the reasoning agent. This prevents the common failure mode of high-similarity but low-relevance retrievals from polluting the generation context. A DuckDuckGo fallback activates when local KB coverage is insufficient, with retrieved content passed through the same reranking pipeline before use.</p>
        </div>
        <div class="project-spec">
          <div class="spec-row"><span class="spec-key">Status</span><span class="spec-val"><span class="ok">Production</span></span></div>
          <div class="spec-row"><span class="spec-key">Agents</span><span class="spec-val">Initializer · Orchestrator · Reasoner</span></div>
          <div class="spec-row"><span class="spec-key">Retrieval</span><span class="spec-val">FAISS multi-KB · semantic reranking</span></div>
          <div class="spec-row"><span class="spec-key">Fallback</span><span class="spec-val">DuckDuckGo → rerank pipeline</span></div>
          <div class="spec-row"><span class="spec-key">Backend</span><span class="spec-val">Flask · Ollama</span></div>
          <div class="spec-row"><span class="spec-key">Privacy</span><span class="spec-val"><span class="hi">Zero cloud inference</span></span></div>
        </div>
      </div>
    </div>

    <!-- PROJECT 3 -->
    <div class="project">
      <div class="project-header">
        <span class="project-id">SYS-003</span>
        <span class="project-name">Document Intelligence Pipeline</span>
      </div>
      <div class="project-subtitle">Phase 1→2 Ingestion · FAISS Vectorization · Deterministic Outlier Detection</div>
      <div class="project-body">
        <div class="project-desc">
          <p>A two-phase pipeline treating document ingestion and vectorization as separate, versioned concerns. <strong>Phase 1</strong> (ai-train.py) handles multi-format extraction — PDF via pdfplumber with PyPDF2 fallback, DOCX, Tesseract OCR for scanned documents, and web crawl via BeautifulSoup — producing structured JSONL with preserved metadata: doc_id, source, category, creation timestamp, token count, and LLM-generated summary.</p>
          <p><strong>Phase 2</strong> (merge_vector.py) consumes Phase 1 output and constructs FAISS indices using all-mpnet-base-v2 at 768 dimensions. Outlier detection applies mean/std distance thresholding across the full embedding space before index construction — documents with embedding distance exceeding 3.0σ from the corpus mean are flagged and excluded, preventing retrieval contamination from anomalous documents. Indices and metadata maps are versioned with timestamps and stored to a structured vault.</p>
        </div>
        <div class="project-spec">
          <div class="spec-row"><span class="spec-key">Status</span><span class="spec-val"><span class="ok">Production</span></span></div>
          <div class="spec-row"><span class="spec-key">Phase 1</span><span class="spec-val">PDF · DOCX · OCR · Web crawl</span></div>
          <div class="spec-row"><span class="spec-key">Phase 2</span><span class="spec-val">FAISS · all-mpnet-base-v2 · 768D</span></div>
          <div class="spec-row"><span class="spec-key">Outlier</span><span class="spec-val">Mean/std · 3.0σ threshold</span></div>
          <div class="spec-row"><span class="spec-key">API</span><span class="spec-val">Flask · /vectorize · /topk</span></div>
          <div class="spec-row"><span class="spec-key">Versioning</span><span class="spec-val">Timestamped vault · pkl metadata</span></div>
        </div>
      </div>
    </div>

    <!-- PROJECT 4 -->
    <div class="project">
      <div class="project-header">
        <span class="project-id">SYS-004</span>
        <span class="project-name">Sovereign Coding Assistant</span>
      </div>
      <div class="project-subtitle">Three-Brain Architecture · Persistent RAG Memory · Five-Layer AST Validation</div>
      <div class="project-body">
        <div class="project-desc">
          <p>Built in direct response to the documented failure modes of commercial coding assistants: context loss across sessions, hallucinated function signatures, overconfident refactoring that destroys working code, and the structural incentive to maximize token consumption. The system implements a three-brain architecture where cognitive tasks are routed to purpose-specific models: a 1B Organizer for intent classification, a 7B Coding Brain for generation and refactoring, and a 3B Reasoning Brain for logic verification and security review.</p>
          <p>Codebase memory is maintained in a FAISS-backed RAG vault using nomic-embed-text embeddings. Session state is strictly isolated per feature to prevent cross-contamination. A five-layer validation pipeline processes all generated code before persistence: Python AST compilation, style analysis, heuristic linting, security scanning (eval/exec detection, secrets), and hallucination detection via function preservation analysis and import consistency scoring.</p>
          <p>Stress testing demonstrated 100% context retention over 2+ hour sessions with under 2GB RAM utilization on an Intel i3 with 36GB RAM — no GPU required.</p>
        </div>
        <div class="project-spec">
          <div class="spec-row"><span class="spec-key">Status</span><span class="spec-val"><span class="ok">Daily Use</span></span></div>
          <div class="spec-row"><span class="spec-key">Brains</span><span class="spec-val">1B router · 7B coder · 3B verifier</span></div>
          <div class="spec-row"><span class="spec-key">Memory</span><span class="spec-val">FAISS · nomic-embed-text</span></div>
          <div class="spec-row"><span class="spec-key">Validation</span><span class="spec-val">AST · Style · Lint · Sec · Halluc</span></div>
          <div class="spec-row"><span class="spec-key">RAM</span><span class="spec-val">&lt;2GB active · 36GB total</span></div>
          <div class="spec-row"><span class="spec-key">Hardware</span><span class="spec-val">Intel i3 · No GPU</span></div>
        </div>
      </div>
    </div>

    <!-- PROJECT 5 -->
    <div class="project">
      <div class="project-header">
        <span class="project-id">SYS-005</span>
        <span class="project-name">Sovereign Invoice Audit Engine</span>
      </div>
      <div class="project-subtitle">Financial Document AI · Semantic Price Matching · Variance Detection · WebSocket Streaming</div>
      <div class="project-body">
        <div class="project-desc">
          <p>A dual-agent financial document analysis system targeting the specific problem of invoice variance detection against master pricing databases. The Auditor agent extracts line items, quantities, and amounts from submitted invoices. The Narrator agent generates human-readable audit narratives. A <strong>SovereignMatcher</strong> component performs semantic matching between extracted invoice items and master pricing records using SentenceTransformer embeddings — handling the real-world problem of inconsistent vendor naming conventions that defeat exact-match approaches.</p>
          <p>A vision model fallback (LLaMA 3.2-vision) handles non-digital PDFs where standard extraction yields insufficient text density. WebSocket connections stream live audit log events to the client, providing real-time visibility into multi-document processing pipelines. Dynamic column mapping handles header variance across different vendor invoice formats without schema reconfiguration.</p>
        </div>
        <div class="project-spec">
          <div class="spec-row"><span class="spec-key">Status</span><span class="spec-val"><span class="ok">Production</span></span></div>
          <div class="spec-row"><span class="spec-key">Matching</span><span class="spec-val">SentenceTransformer · cosine sim</span></div>
          <div class="spec-row"><span class="spec-key">Fallback</span><span class="spec-val">LLaMA 3.2-vision OCR</span></div>
          <div class="spec-row"><span class="spec-key">Streaming</span><span class="spec-val">WebSocket live audit log</span></div>
          <div class="spec-row"><span class="spec-key">Backend</span><span class="spec-val">FastAPI · Pandas · NumPy</span></div>
          <div class="spec-row"><span class="spec-key">Privacy</span><span class="spec-val"><span class="hi">Air-gap capable</span></span></div>
        </div>
      </div>
    </div>

    <!-- PROJECT 6 -->
    <div class="project">
      <div class="project-header">
        <span class="project-id">SYS-006</span>
        <span class="project-name">Red Team Auditor</span>
      </div>
      <div class="project-subtitle">Dynamic Code Hardening · CAG + RAG · CVE Integration · Adaptive LoRA · Reflex Buffer</div>
      <div class="project-body">
        <div class="project-desc">
          <p>A production cybersecurity hardening pipeline combining CAG (Cache-Augmented Generation) with RAG retrieval, live CVE database integration, and adaptive LoRA for pattern learning. Three specialized personas — <strong>Auditor</strong> (vulnerability detection, credential exposure, weak cryptography), <strong>Hardener</strong> (secure alternative proposals, defense-in-depth), and <strong>Architect</strong> (systemic design pattern analysis) — operate on a shared ChromaDB knowledge base built with LlamaIndex and mxbai-embed-large embeddings.</p>
          <p>The Reflex Buffer maintains a persistent JSON store of analyst-approved findings, enabling the system to accumulate institutional knowledge across engagements. CVE cache refresh logic enforces a 24-hour staleness threshold, with NVD rate limiting at 5 requests per 30-second window. The Statistical Governor applies variance-based decision logic across a 50-sample history deque for forensic confidence scoring. A PyTorch-backed LoRA layer enables adaptive weight updates from approved security findings.</p>
        </div>
        <div class="project-spec">
          <div class="spec-row"><span class="spec-key">Status</span><span class="spec-val"><span class="ok">Production</span></span></div>
          <div class="spec-row"><span class="spec-key">Architecture</span><span class="spec-val">CAG + RAG · ChromaDB · LlamaIndex</span></div>
          <div class="spec-row"><span class="spec-key">Personas</span><span class="spec-val">Auditor · Hardener · Architect</span></div>
          <div class="spec-row"><span class="spec-key">CVE</span><span class="spec-val">NVD live · 24hr cache · rate limited</span></div>
          <div class="spec-row"><span class="spec-key">Learning</span><span class="spec-val">Reflex Buffer · adaptive LoRA</span></div>
          <div class="spec-row"><span class="spec-key">Scoring</span><span class="spec-val">Statistical Governor · 50-sample deque</span></div>
        </div>
      </div>
    </div>

    <!-- PROJECT 7 -->
    <div class="project">
      <div class="project-header">
        <span class="project-id">SYS-007</span>
        <span class="project-name">Forensic Identity Replication Pipeline</span>
      </div>
      <div class="project-subtitle">Adaptive LoRA Training · Cosine Drift Verification · Multi-Pass Stable Diffusion Inference</div>
      <div class="project-body">
        <div class="project-desc">
          <p>A fully offline pipeline for forensic-grade facial identity preservation in generative image synthesis. The system targets the specific failure mode of stylization drift — the tendency of generative models to replace anatomical specificity with aesthetic idealization. The pipeline locks identity from a single source image and verifies retention quantitatively at each stage.</p>
          <p>Training employs a four-phase adaptive LoRA regime with phase-specific loss functions: MSE (COARSE, α=8), Huber (MID, α=4), and Charbonnier (MID_FINE and FINAL_FINE, α=2/1). Early exit is governed by Welford online mean/variance tracking, sliding-window slope analysis, and p-value plateau detection — the system exits each phase on verified statistical convergence, not fixed step counts. Post-training seed verification generates candidate renders across multiple seeds and computes cosine distance between a 512-dimensional reference embedding and each generated output. Renders with drift exceeding 0.18 are rejected. The locked seed is fixed for all downstream stylized inference.</p>
        </div>
        <div class="project-spec">
          <div class="spec-row"><span class="spec-key">Status</span><span class="spec-val"><span class="ok">Production</span></span></div>
          <div class="spec-row"><span class="spec-key">Training</span><span class="spec-val">4-phase LoRA · MSE→Huber→Charb.</span></div>
          <div class="spec-row"><span class="spec-key">Convergence</span><span class="spec-val">Welford · slope · p-value plateau</span></div>
          <div class="spec-row"><span class="spec-key">Verification</span><span class="spec-val">512-D cosine drift · threshold ≤0.18</span></div>
          <div class="spec-row"><span class="spec-key">Inference</span><span class="spec-val">3-pass dynamic · 2-pass stylizer</span></div>
          <div class="spec-row"><span class="spec-key">Input</span><span class="spec-val">Single source image</span></div>
          <div class="spec-row"><span class="spec-key">Privacy</span><span class="spec-val"><span class="hi">Fully offline</span></span></div>
        </div>
      </div>
    </div>

  </section>

  <!-- ── SECTION 3: PUBLICATION ─────────────────────────── -->
  <section class="section fade d4">
    <div class="section-header">
      <span class="section-num">§ 03</span>
      <div class="section-rule"></div>
      <span class="section-title">Research Publication</span>
    </div>
    <div class="publication">
      <div class="pub-label">Peer-Reviewable Technical Paper · 2024</div>
      <div class="pub-title">Identity Preservation in Generative Image Synthesis: A Forensic-Grade, LoRA-Based Facial Replication Framework</div>
      <div class="pub-meta">Todd M. Lipscomb · TML Investments LLC · github.com/Todd2112/My-Portfolio</div>
      <div class="pub-abstract">Presents a fully offline pipeline for forensic-grade replication of human facial identity from minimal image data. Unlike generative systems emphasizing stylization, this framework locks anatomical identity from real-world photographs and preserves geometric integrity across varying environments, lighting conditions, and render styles. Introduces 4-phase adaptive LoRA convergence with Welford statistical tracking and p-value plateau detection; cosine drift scoring for quantitative identity verification post-training; and multi-pass Stable Diffusion rendering from single-image input. Demonstrates drift ≤ 0.1621 across diverse scene conditions including outdoor golden-hour, indoor natural light, and environmental occlusion scenarios. All operations performed on-device with no cloud dependencies.</div>
    </div>
  </section>

  <!-- ── SECTION 4: TECHNICAL STACK ────────────────────── -->
  <section class="section fade d5">
    <div class="section-header">
      <span class="section-num">§ 04</span>
      <div class="section-rule"></div>
      <span class="section-title">Technical Stack &amp; System Specifications</span>
    </div>
    <div class="stack-matrix">
      <div class="stack-col">
        <div class="stack-col-label">Inference &amp; ML</div>
        <div class="stack-item"><span class="dot">▸</span>Ollama · LLaMA 3.2 (1B/3B/7B)</div>
        <div class="stack-item"><span class="dot">▸</span>FAISS · IndexFlatL2</div>
        <div class="stack-item"><span class="dot">▸</span>Sentence Transformers</div>
        <div class="stack-item"><span class="dot">▸</span>all-mpnet-base-v2 · 768D</div>
        <div class="stack-item"><span class="dot">▸</span>nomic-embed-text</div>
        <div class="stack-item"><span class="dot">▸</span>mxbai-embed-large</div>
        <div class="stack-item"><span class="dot">▸</span>Stable Diffusion · LoRA</div>
        <div class="stack-item"><span class="dot">▸</span>PyTorch · AdamW · AdamP</div>
        <div class="stack-item"><span class="dot">▸</span>ChromaDB · LlamaIndex</div>
        <div class="stack-item"><span class="dot">▸</span>Welford Online Statistics</div>
      </div>
      <div class="stack-col">
        <div class="stack-col-label">Backend &amp; APIs</div>
        <div class="stack-item"><span class="dot">▸</span>Python 3.10+</div>
        <div class="stack-item"><span class="dot">▸</span>FastAPI · asyncio · uvicorn</div>
        <div class="stack-item"><span class="dot">▸</span>Flask · Werkzeug</div>
        <div class="stack-item"><span class="dot">▸</span>WebSocket · SSE streaming</div>
        <div class="stack-item"><span class="dot">▸</span>Pydantic v2 · model_validator</div>
        <div class="stack-item"><span class="dot">▸</span>httpx · async HTTP</div>
        <div class="stack-item"><span class="dot">▸</span>Pandas · NumPy · SciPy</div>
        <div class="stack-item"><span class="dot">▸</span>Python AST · compile()</div>
        <div class="stack-item"><span class="dot">▸</span>SQLite · JSONL pipelines</div>
        <div class="stack-item"><span class="dot">▸</span>Pickle · versioned vault I/O</div>
      </div>
      <div class="stack-col">
        <div class="stack-col-label">Document &amp; Security</div>
        <div class="stack-item"><span class="dot">▸</span>pdfplumber · PyPDF2 · pypdf</div>
        <div class="stack-item"><span class="dot">▸</span>Tesseract OCR · pdf2image</div>
        <div class="stack-item"><span class="dot">▸</span>python-docx · BeautifulSoup</div>
        <div class="stack-item"><span class="dot">▸</span>Pillow · PIL image pipeline</div>
        <div class="stack-item"><span class="dot">▸</span>NVD CVE API · live feed</div>
        <div class="stack-item"><span class="dot">▸</span>AST security scanning</div>
        <div class="stack-item"><span class="dot">▸</span>OS firewall · air-gap controls</div>
        <div class="stack-item"><span class="dot">▸</span>SpaCy · TextStat · NLP</div>
        <div class="stack-item"><span class="dot">▸</span>DuckDuckGo search API</div>
        <div class="stack-item"><span class="dot">▸</span>dotenv · secrets management</div>
      </div>
    </div>
  </section>

  <!-- ── SECTION 5: CREDENTIALS ────────────────────────── -->
  <section class="section fade d5">
    <div class="section-header">
      <span class="section-num">§ 05</span>
      <div class="section-rule"></div>
      <span class="section-title">Formal Credentials</span>
    </div>
    <table class="cred-table">
      <thead>
        <tr>
          <th>Issuing Body</th>
          <th>Credential</th>
          <th>Issued</th>
          <th>Verify</th>
        </tr>
      </thead>
      <tbody>
        <tr><td class="issuer">Stanford University</td><td class="cert-name">Machine Learning Specialization (3 courses — Andrew Ng)</td><td class="date">2024</td><td>—</td></tr>
        <tr><td class="issuer">IBM</td><td class="cert-name">Generative AI: Prompt Engineering Basics</td><td class="date">Jul 2024</td><td><a href="https://coursera.org/verify/CJ2A5CL8J6HP" target="_blank">↗</a></td></tr>
        <tr><td class="issuer">IBM</td><td class="cert-name">Generative AI: Boost Your Cybersecurity Career</td><td class="date">Jul 2024</td><td>—</td></tr>
        <tr><td class="issuer">IBM</td><td class="cert-name">Cybersecurity Capstone: Breach Response Case Studies</td><td class="date">Apr 2024</td><td>—</td></tr>
        <tr><td class="issuer">Cisco</td><td class="cert-name">Security Operations Center (SOC) Specialization — 7 courses</td><td class="date">2024</td><td>—</td></tr>
        <tr><td class="issuer">Cisco</td><td class="cert-name">Threat Analysis</td><td class="date">Jun 2024</td><td><a href="https://coursera.org/verify/P5M7APQDVMXH" target="_blank">↗</a></td></tr>
        <tr><td class="issuer">Cisco / IBM</td><td class="cert-name">Data Security</td><td class="date">Jun 2024</td><td><a href="https://coursera.org/verify/9N6GGAJ9XTTX" target="_blank">↗</a></td></tr>
        <tr><td class="issuer">Google</td><td class="cert-name">System Administration and IT Infrastructure Services</td><td class="date">Dec 2023</td><td><a href="https://coursera.org/verify/2WGQWWZFXKNV" target="_blank">↗</a></td></tr>
        <tr><td class="issuer">Google</td><td class="cert-name">Operating Systems and You: Becoming a Power User</td><td class="date">Dec 2023</td><td><a href="https://coursera.org/verify/QKP8FZ8VMHDC" target="_blank">↗</a></td></tr>
        <tr><td class="issuer">University of Michigan</td><td class="cert-name">Python 3 Programming Specialization — 5 courses</td><td class="date">Jan 2025</td><td>—</td></tr>
        <tr><td class="issuer">University of Michigan</td><td class="cert-name">Python Classes and Inheritance</td><td class="date">Jan 2025</td><td>—</td></tr>
        <tr><td class="issuer">University of Michigan</td><td class="cert-name">Data Collection and Processing with Python</td><td class="date">Jan 2025</td><td>—</td></tr>
        <tr><td class="issuer">University of Michigan</td><td class="cert-name">Python Functions, Files, and Dictionaries</td><td class="date">Nov 2024</td><td>—</td></tr>
      </tbody>
    </table>
  </section>

  <!-- ── SECTION 6: POSITION STATEMENT ─────────────────── -->
  <section class="section fade d6">
    <div class="section-header">
      <span class="section-num">§ 06</span>
      <div class="section-rule"></div>
      <span class="section-title">Engineering Position</span>
    </div>
    <div class="position">
      <p>The commercial AI industry has a structural problem it does not advertise: the failure modes it leaves unsolved are the same ones that generate recurring revenue. Context that expires requires re-injection. Hallucination that persists requires human correction. Stateless inference requires continued API access. These are not bugs awaiting patches. They are architectural decisions with balance sheet implications.</p>
      <p>The systems documented here were built from the opposing premise — that <strong>a $700 laptop running carefully architected local inference can outperform a $90/month cloud subscription</strong> for specific, high-stakes tasks, provided the engineering addresses the actual failure modes rather than papering over them with scale. The evidence is in the implementations: 100% context retention over multi-hour sessions, verified zero data egress, drift-locked identity replication from single-image input, and financial document analysis without a single byte transmitted to an external server.</p>
      <p>This is not anti-technology. It is <strong>pro-verification</strong>. Every architectural claim made here is testable. Every system documented here is running. The future of reliable AI inference is not in larger models or higher-bandwidth APIs. It is in better engineering of the systems that sit between the model and the task.</p>
    </div>
  </section>

  <!-- ── CONTACT ────────────────────────────────────────── -->
  <section class="section fade d6">
    <div class="section-header">
      <span class="section-num">§ 07</span>
      <div class="section-rule"></div>
      <span class="section-title">Contact &amp; Engagement</span>
    </div>
    <div class="contact-grid">
      <div class="contact-item">
        <div class="contact-label">Email</div>
        <div class="contact-value"><a href="mailto:realtodd@yahoo.com">realtodd@yahoo.com</a></div>
      </div>
      <div class="contact-item">
        <div class="contact-label">GitHub</div>
        <div class="contact-value"><a href="https://github.com/Todd2112" target="_blank">github.com/Todd2112</a></div>
      </div>
      <div class="contact-item">
        <div class="contact-label">LinkedIn</div>
        <div class="contact-value"><a href="https://linkedin.com/in/todd-lipscomb-670458290" target="_blank">todd-lipscomb-670458290</a></div>
      </div>
      <div class="contact-item">
        <div class="contact-label">Freelance</div>
        <div class="contact-value"><a href="https://upwork.com" target="_blank">Upwork · TML Investments LLC</a></div>
      </div>
    </div>
  </section>

  <!-- ── FOOTER ─────────────────────────────────────────── -->
  <footer class="footer fade d6">
    <span>TODD M. LIPSCOMB · TML INVESTMENTS LLC · TRENTON, MI</span>
    <span id="build"></span>
  </footer>

</div>
<script>
  function tick() {
    const now = new Date();
    document.getElementById('ts').textContent =
      now.toUTCString().replace(' GMT','') + ' UTC';
  }
  tick(); setInterval(tick, 1000);
  document.getElementById('build').textContent =
    'REV ' + new Date().toISOString().slice(0,10).replace(/-/g,'.');
</script>
</body>
</html>
