import streamlit as st
import requests

# App Title
st.set_page_config(page_title="Reasoning AI Chatbot", layout="centered")
st.title("🧠 Reasoning AI Chatbot")

# Mode Toggle
mode = st.radio("Choose a mode:", ["Demo Mode (No Ollama)", "Full Mode (Ollama Required)"])
use_demo_mode = mode == "Demo Mode (No Ollama)"

# Function to check if Ollama is running
def is_ollama_running():
    try:
        response = requests.get("http://127.0.0.1:11434")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Handle Full Mode connection check
if not use_demo_mode:
    if not is_ollama_running():
        st.error("❌ Could not connect to Ollama.\n\nMake sure it's running using:\n\n```bash\nollama serve\n```\n")
        st.stop()

# Prompt Input
prompt = st.text_area("Enter your prompt:", height=150)
submit = st.button("🧠 Run Reasoning")

# Handle Button Click
if submit and prompt:
    with st.spinner("Thinking..."):
        try:
            if use_demo_mode:
                # Fake response for demo
                st.success("✅ This is a demo response. Replace this with your real Ollama output.")
            else:
                # Send prompt to Ollama
                response = requests.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={"model": "deepseek-coder:1.3b", "prompt": prompt}
                )
                response.raise_for_status()
                result = response.json()["response"]
                st.success(result)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Ollama request failed: {e}")
