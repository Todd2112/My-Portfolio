My Journey with AI: From Stateless Agents to Domain Memory

For years, I pushed AI systems like ChatGPT, Gemini, and Claude to handle real work, not toy examples. I asked them to code, reason, and plan — over projects that couldn't tolerate amnesia. And every single time, I hit the same wall: they forgot. They lost context between sessions, hallucinated progress, redefined tasks midstream, and broke continuity whenever complexity grew.

The breaking point was coding. Software is unforgiving: one misplaced line, one inconsistent assumption, and everything collapses. Concepts must remain consistent, unfinished work must resume exactly where it left off, and progress must be cumulative. That's when I realized: the problem isn't the models — it's asking stateless systems to behave like stateful engineers.

The Foundation: Why I Could See What Others Missed

My insight didn't come overnight. It was built on years of study across the AI stack:

Machine Learning Fundamentals (Stanford/DeepLearning.AI): Supervised and unsupervised learning, neural networks, decision trees, recommender systems, reinforcement learning. I didn't just use AI — I understood how it works under the hood. When LLMs failed at long-horizon tasks, I knew it was a stateless architecture problem, not a capability problem.

Python Engineering (University of Michigan): Beyond syntax, I mastered software engineering principles — classes, inheritance, data structures, API design. Building persistent memory systems demanded this level of rigor.

Cybersecurity Operations (Cisco): SOC operations, threat analysis, network security, incident response. Security analysts rely on logs and institutional memory — the discipline of stateful systems informed how I designed AI memory infrastructure.

System Administration & IT (Google): Operating systems, production infrastructure, hardware optimization. These skills allowed me to build local-first, hardware-optimized AI deployments that don't depend on cloud services.

This combination — theory, engineering, security, and systems thinking — let me see clearly: commercial AI platforms were optimizing model intelligence when they should have been engineering memory.

The Turning Point: Domain Memory

The breakthrough came when I stopped trying to make AI "smarter" and started structuring work around memory. You can start with a strong coding agent — Gemini, Claude, or any capable LLM — inside a harness with context compaction, planning, and execution. But in practice, that alone doesn't work. Without domain memory, even the most capable agent is an amnesiac.

Domain memory is the bridge to serious, long-running AI agents. It's not a vector database to "query." It's a persistent, structured, stateful representation of the work itself, ensuring every run picks up exactly where it left off. Within a domain, you need:

Persistent goals across sessions

Explicit feature lists marking done vs. pending

Requirements and constraints guiding decisions

Passing/failing states — no ambiguity

A record of attempts, reversions, completions

Scaffolding for execution, testing, and extension

This can be JSON blobs, progress logs, and test harnesses. The agent's role becomes simple: pick a failing feature, implement it, run tests, mark passing, commit progress. It reads the scaffolding and instantly knows its context.

Memory isn't incidental — it's the ground truth.

Long-running AI succeeds not through intelligence, but through disciplined memory management. My SOC training made this obvious: analysts don't start each shift asking "what happened yesterday?" They consult logs. AI agents need the same architecture.

The Battle Story: Proof the Architecture Works

Over the course of three years, I relentlessly tested every approach the commercial AI world offered:

Hundreds of hours of trying every prompt, every chain-of-thought hack, and every “world-class expert” trick.

Billions in infrastructure and cloud services that still failed to maintain project continuity.

my_coder.py, a working proof-of-concept, became the testbed for domain memory, three-agent orchestration, and iterative execution.

The journey wasn’t clean. Agents hallucinated, sessions drifted, features got lost. Each failure taught a lesson: more parameters don't fix memory; better prompting doesn’t create persistence. The environment had to be engineered around memory, not the agent around cleverness.

With my_coder.py, I finally achieved:

Persistent feature tracking across multiple sessions.

Atomic execution of features with verification before committing.

Seamless recovery from failed or partial runs.

Strict separation of chat and code to prevent narrative contamination.

This wasn’t theory. This was working AI that could actually complete long-horizon tasks, resume exactly where it left off, and do so reliably with multiple models — locally, safely, and reproducibly.

The Code vs. Chat Problem

A deceptively hard challenge emerged: distinguishing code from conversation. Code has syntax, but LLM outputs blend commentary, suggestions, and snippets. Without strict separation, pipelines break: narrative treated as code, code discarded as commentary, half-baked snippets corrupt execution.

Key components affected:

Editor as source of truth: All edits are definitive. Divergence from memory creates conflicts.

Intent detection: Classify requests (modify, review, fix, explain, discuss) and validate targets. Misclassification is destructive.

Code extraction: Strip markdown, narrative, and commentary reliably.

Memory integration: CAG and RAG engines require precise separation; conflating chat and code poisons reasoning.

Solutions:

Robust extraction routines with fallback strategies

Feature-scoped workflows targeting a single piece of work

Symbol table analysis using AST parsing

Streaming responses separating narrative, code, and verification

This separation became architectural. Iterative reasoning became reliable; without it, sessions drift into chaos.

The Three-Agent Pattern: Memory as Infrastructure

Through trial and error, I converged on a three-agent pattern that makes memory explicit:

1. Initializer Agent

Transforms high-level intent into executable structure.

Decomposes prompts into detailed, testable feature lists

Bootstraps domain memory

Defines "done" criteria and engagement rules

Sets up scaffolding for future runs

Stateless by design. Think of it as writing the constitution before the government operates. It doesn't need memory — its job is to create the memory structure.

2. Coding Agent

Executes one atomic task, then disappears.

Reads domain memory

Picks a failing feature

Implements and tests

Updates status and logs progress

Vanishes

Deliberately amnesiac. Long-running LLM memory doesn't work. Instead, memory lives in the environment — the scaffolding, not the agent. Each run starts fresh but with perfect context from the harness.

3. Reasoning & Validation Agent

Ensures quality and compliance.

Validates syntax and logic

Confirms feature solves the stated problem

Updates domain memory

Disappears

The Core Insight:

The magic isn't in the agents — it's in the harness.

The agents themselves can be simple. What matters is engineering the environment for success. Stop trying to make agents smarter. Make the environment smarter, and simple agents deliver complex results.

Why Commercial AI Gets It Wrong

Platforms like ChatGPT, Gemini, Claude, and cloud AI fail at serious work because they optimize for:

Model intelligence (bigger, faster, more parameters)

Subscription revenue (lock-in through monthly fees)

Centralized infrastructure (your data on their servers)

General-purpose capability (one agent for everything)

They ignore the key problem: without domain memory, every session is a disconnected intern guessing what happened last time.

Consequences:

Lost context between sessions

No durable project state

Chat/code conflation

Repeated reinvention of "done"

Your data feeds their models while you rent access

The Data Sovereignty Problem:

Every prompt you send, every codebase you feed — that's reconnaissance data for their models. They profile, learn, and monetize your work. If you stop paying, you lose everything.

Why This Matters: The Architecture Generalizes

This memory-centric, three-agent architecture isn't limited to code. The same principles apply to:

Contracts and legal documents — maintain versioned states, track clauses, detect regressions.

Medical records — longitudinal updates, patient history consistency, compliance checks.

Financial models — iterative simulations, audit trails, reproducibility.

Research workflows — data, analysis, code, and notes persist and interconnect.

Domain memory + strict separation + iterative agents provides a scalable, reliable pattern for any domain where continuity, correctness, and context matter.

Lessons Learned

Long-horizon failure = memory, not intelligence. More parameters won't fix forgetfulness.

Prompting = environment initialization. The best prompts establish context, constraints, and scaffolding.

Memory ownership is critical. Context window memory evaporates. Persistent artifact memory accumulates.

Domain memory enforces discipline. With proper scaffolding, agents behave like engineers, not autocomplete.

Separation of concerns scales. One agent to initialize, one to execute, one to validate. Each simple, each effective.

The harness is the innovation, not the agent. Engineer the environment right, and simple agents deliver complex results.

Structured this way, AI stops guessing. Each run is cumulative, consistent, and grounded — exactly like a disciplined engineer.

The Bottom Line

Clients don't need a sales pitch. They need proof of capability.

This journey — from frustration with commercial AI, to formal education across the AI stack, to insight about memory architecture, to disciplined system engineering — demonstrates that expertise isn't in prompting a clever agent.

The expertise is in knowing how to build AI that remembers, progresses, and behaves like a professional engineer with institutional memory.

My credentials span:

Machine Learning (Stanford/DeepLearning.AI)

Python Software Engineering (University of Michigan)

Cybersecurity Operations (Cisco)

System Administration (Google)

Generative AI & Prompt Engineering (IBM)

This is production-grade system architecture informed by years of study and hardened by real-world problem-solving.

I’ve built AI that actually works over weeks and months, across domains, on local hardware, without cloud, subscriptions, or vendor lock-in.
