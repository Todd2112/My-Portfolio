## 🔍 Solving the Black Box Problem in AI Coding

This app is a **proof of concept** for a more transparent and reliable way to interact with AI coding assistants. Instead of blindly generating Python code, it first explains its reasoning — giving you visibility into the AI’s logic *before* any code is written.

The goal is twofold:
- Help users **understand and trust** what the AI is doing
- Offer a **debug-first mindset**, where errors can be caught in the logic before they appear in the output

Whether you're a learner, developer, or technical reviewer, this tool showcases how step-by-step reasoning can improve AI reliability, usability, and educational value.

---

### ❓ The Problem

When most AI coding tools generate code, they don’t explain *how* they got there.

You enter a Python question, and it jumps straight to a solution. But:

- Was the question fully understood?
- Were the correct assumptions made?
- Did the logic follow a valid path?

If the AI makes a mistake in reasoning, the code will be flawed — sometimes subtly, sometimes critically. And because the thinking is hidden, **you won’t know until it fails**.

This creates a **black box problem**: we get output, but not insight.  
It makes debugging harder, learning slower, and trust weaker.

---

### ✅ Our Solution: Force the Thinking to the Surface

This app is designed to expose the AI's thought process *before* any code is written.

We achieve that with a carefully crafted system prompt, instructing the AI to always respond in two structured parts:

1. **Reasoning:** A clear explanation of how it's interpreting the question and approaching the solution  
2. **Code:** The actual Python code that follows from the reasoning

```markdown
**Reasoning:**
[Explanation of logic]

**Code:**
```python
[Python Code]
