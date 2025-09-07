# A Framework for an Adaptive, Self-Correcting AI System with Human-in-the-Loop Feedback

## Abstract

Large language models (LLMs) often excel at general conversation but can be unreliable for domain-specific tasks due to a propensity for factual errors and hallucinations. This paper presents a novel architectural framework for an adaptive AI system designed to mitigate these issues. The core of this framework is a local, self-correcting algorithm that grounds LLM output in a user-maintained knowledge base. The system integrates a conversational onboarding process, real-time semantic validation, and a human-in-the-loop feedback mechanism to achieve continuous learning with minimal user friction. We detail the methodology, algorithmic components, and key optimizations that culminate in a stable, accurate, and production-ready system capable of operating entirely offline.

## 1. Introduction & Objective

The objective of this work was to develop an intelligent assistant capable of providing highly accurate, reliable, and verifiable answers for a specific user and their professional domain. A fundamental challenge in deploying LLMs for specialized applications is the lack of guaranteed factual accuracy. Unlike a search engine, an LLM may generate a confident-sounding but entirely fabricated response—a phenomenon known as hallucination.

To overcome this, we created a closed-loop system that operates locally and is continuously refined by the user's explicit, corrective feedback. Our primary goal was to achieve this without burdening the user with a lengthy, manual training process. The system is designed to learn organically from interactions rather than requiring dedicated, resource-intensive training.

## 2. Methodology & Architectural Framework

Our solution is built upon a three-part architecture: a local knowledge base, a self-correction algorithm, and a conversational human-in-the-loop (HITL) feedback mechanism.

### 2.1 The Local Knowledge Base

The system's foundational knowledge is stored in a local SQLite database. Each entry is a document containing a query-answer pair. Crucially, each document also stores a numerical vector representation for both the query and the answer, derived from a pre-trained spaCy embedding model.

Caching these vectors as NumPy arrays in memory at startup provides an efficient lookup mechanism for subsequent operations. This design ensures the entire system can function offline and scales reliably as knowledge is accumulated.

### 2.2 The Self-Correction Algorithm

At the heart of the framework is a scientific algorithm designed to prevent hallucinations and validate output. A user query propagates through a three-phase process:

#### Phase 1: Direct Knowledge Retrieval

The system first performs a direct lookup in the local database. If an exact match is found, the verified answer is returned instantly with a confidence score of 1.0. This bypasses the LLM entirely and ensures immediate reliability.

#### Phase 2: LLM Generation & Semantic Validation

If no direct match exists, the system sends the query to the LLM (Ollama). The prompt includes a system-level instruction based on the user's onboarding context. The LLM's raw output is then validated using drift detection against the top-k most semantically similar entries in the knowledge base.

The **Drift Score** \(D\) is calculated as a composite measure of semantic and token-based divergence:

$$
D = \frac{1}{2} \left[
\bigl(1 - \text{cosine similarity}(V_R, V_{A_k})\bigr) +
\left(1 - \frac{|tokens(R) \cap tokens(A_k)|}{|tokens(R) \cup tokens(A_k)|}\right)
\right]
$$

Where \(V_R\) and \(V_{A_k}\) are the vector embeddings of the raw response and the known answer, respectively. A higher drift score indicates a greater potential for hallucination.

#### Phase 3: Self-Correction Loop

The final **Confidence Score** \(C_f\) is computed as:

$$
C_f = \min \Bigl( 1.0, \max \bigl( 0.0, C_r \times (1 - D) \bigr) \Bigr)
$$

Where \(C_r\) is the raw LLM confidence. If \(C_f\) falls below a predefined threshold (e.g., 0.9) or if \(D > 0.6\), the system re-prompts the LLM with the original query and prior response, instructing it to refine its answer. This loop is limited to two iterations to balance accuracy and performance.

### 2.3 Human-in-the-Loop Feedback

When confidence is low or the AI responds with "I don't know," a feedback form is presented to the user. Any correction is immediately:

- Saved to the knowledge base  
- Vectorized for semantic retrieval  
- Added to the in-memory cache  

This ensures that the AI learns precisely when and where it needs to, preventing repeated uncertainty on the same topic.

## 3. Results & Achievements

The methodology culminates in a practical and effective AI system. Key achievements include:

- **Zero-Friction Onboarding:** A simple, conversational four-question flow replaces hours of manual training. Subsequent learning happens naturally during use.  
- **Effective Hallucination Mitigation:** The Drift Detection Algorithm reliably identifies ungrounded information.  
- **Operational Efficiency:** Pre-cached vectors and optimized self-correction loops enable responsive performance even with a growing knowledge base.  
- **User-Centric Design:** Uncertain sentences are highlighted, and feedback forms make learning intuitive and minimally disruptive.

**Example Workflow:**

1. User asks: "How do I process large datasets in Python?"  
2. Knowledge base has no match → LLM generates response  
3. Semantic drift evaluated → Confidence < threshold  
4. AI responds: "I don't know, what is it?"  
5. User provides correct answer → Stored in DB → Next response is confident

## 4. Conclusion

We have developed a robust, production-ready framework for a self-correcting AI assistant. By grounding an LLM’s output in a local, verifiable knowledge base and integrating a seamless human-in-the-loop feedback mechanism, the system is:

- **Fast:** Onboarding takes only a few minutes  
- **Intuitive:** Learning occurs naturally during conversation  
- **Reliable:** Drift detection prevents hallucinations  

This framework provides a practical solution to LLM hallucinations and sets a new standard for trusted, domain-specific AI applications.
