# Sovereign Legal Engine: Entry 01 in the Sovereign Series

**"Local AI for High-Stakes Law—No APIs, No Data Leaks, No Compromises."**

I built the **Sovereign Legal Engine** because the legal industry has a massive problem: they are being told that high-level AI reasoning only exists in the cloud. For a senior litigator or an appellate clerk, sending sensitive filings to a 3rd-party API isn't just a risk—it's a liability. 

This isn't a "wrapper." It’s a precision-engineered audit tool that runs 100% on my own hardware. I designed it to bring "Zero Trust" intelligence directly to your desk.

![Sovereign Discovery Interface](https://github.com/Todd2112/My-Portfolio/raw/master/AI-Your-Way/Sovereign%20Legal%20Engine/SD_pg1.jpg)

---

### End-User Programmability (The Logic Store)
I don't believe in "one size fits all" AI. Every case has a different mission. I built a **Logic Store** into the engine where the end-user defines exactly what the search and prompt outputs will be. 


Here's where the end user defines what the search/prompts outputs will be. I put in a few "pre-made" defaults but since I'm not a lawyer these obviously can be used or more importantly, the end user can apply and create their own prompts. 

Whether I'm doing a deposition summary or a contract review, I just commit the new logic and the engine adapts.

---

### Key Engineering Pillars

#### 1. The Defensive Fallback Chain
I don't trust standard extraction. I built a multi-stage fallback system to prevent "Garbage In, Garbage Out":

![Data Ingestion Process](https://github.com/Todd2112/My-Portfolio/raw/master/AI-Your-Way/Sovereign%20Legal%20Engine/SD_pg3.jpg)

* **Structural Parsing:** First, I try to extract high-fidelity tables and headers.
* **OCR Pivot:** If the text density is too low or garbled, the engine automatically pivots to local OCR.
* **Verification:** I implemented a quality-check layer. If the data isn't clean enough for a courtroom, the system stops. I'd rather give you no answer than a wrong one.

#### 2. The Dual-Agent Pipeline (Auditor vs. Narrator)
I realized that asking one small model to do everything causes "context drift." To solve this, I split the "brain" into two specialized agents running in parallel on my local CPU. 

![Logic Reasoning and Confidence](https://github.com/Todd2112/My-Portfolio/raw/master/AI-Your-Way/Sovereign%20Legal%20Engine/SD_pg4.jpg)

As always, I'm using small pre-trained models on a laptop to bring AI and LLMs to the real world without having to waste money on subscriptions and big GPU-based hardware:
* **The Auditor (Llama 3.2 3B):** This agent is clinical. It focuses strictly on extracting Holdings, Rules, and Precedents into a structured JSON ledger.
* **The Narrator (Llama 3.2 1B):** This agent handles the human side. It generates the brief and handles mission-keyword highlighting (like FSIA or Sovereign Immunity).

#### 3. Zero-Chatter Sanitization
Local models love to "talk" and add conversational fluff. I built a custom sanitization layer that strips away the "AI-ness." No "Sure, here's your analysis." You get the findings, the authority type, and the risk level. Period.

---

### The Discovery Ledger: Structured Truth
The final goal isn't a "chat." It's a structured audit. Below is the final output of the engine—a high-fidelity risk ledger that classifies every legal component by Authority Type and Risk Factor.


### The Sovereign Specs
I’m a firm believer that you shouldn't need a server farm to run powerful AI.
* **Hardware:** Tested and optimized for an M-series Mac or a modern laptop (16GB+ RAM).
* **Inference:** Runs 100% locally via **Ollama**.
* **Privacy:** Air-gapped capable. Your strategy and your data stay where they belong—under your control.

---

### Project Status & Access
**Note:** The Sovereign Legal Engine is a proprietary product. This repository serves as a technical showcase and architectural proof-of-work. 

**If you're interested in the Sovereign Series or want a demo of the engine in action, connect with me on LinkedIn.** https://www.linkedin.com/in/todd-lipscomb-670458290/
