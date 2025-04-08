# 🤖 Reasoning AI Chatbot (Portfolio Demo)

Welcome to my **Reasoning AI Chatbot!**  
This app simulates how an intelligent assistant reasons through your questions — showing both its thought process and final answers.

---

## 🚀 Live Demo for HR Reviewers

[🚀 Click here to try the app (Demo Mode only)](https://my-portfolio-reasoning-ai.streamlit.app)  
_**Tip:** Right-click or Ctrl+Click to open in a new tab!_

Demo Mode gives you a frictionless experience. It mimics how the AI would respond using logical reasoning — even without a large language model installed.

---

## 🧠 Full Mode (Local Use Only)

Want to run this chatbot with full AI power using **Ollama**?

1. **Install Ollama**  
   👉 [Download here](https://ollama.com/download)

2. **Start the Ollama server:**
   ```bash
   ollama serve
3. **Pull a model (e.g., DeepSeek or LLaMA3):**
   ```bash
   ollama pull deepseek-coder:latest
4. **or:**
   ```bash
   ollama pull llama3
5. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit-app.py
In the app, switch to "Full Mode" using the toggle at the top to enable actual AI-based reasoning.
Now your chatbot is connected to a real local LLM!

📦 Dependencies

Make sure these are installed in your Python environment:

**requirements.txt**
```bash
streamlit
requests


