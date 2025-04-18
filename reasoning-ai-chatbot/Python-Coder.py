import streamlit as st
import requests

# Page title
st.set_page_config(page_title="Reasoning AI Chatbot", page_icon="🤖")
st.title("🤖 Reasoning AI Chatbot")

# Mode toggle
mode = st.radio("Choose Mode:", ["Demo Mode (for HR)", "Full Mode (requires Ollama)"])

# Chat input
user_input = st.text_input("Ask a question:")

# Session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Demo Mode behavior
if mode == "Demo Mode (for HR)":
    st.info("💡 You're in Demo Mode. This version simulates the AI's reasoning without needing Ollama.")
    if user_input:
        # Simulated "smart" demo response
        response = f"🤖 (Demo): Great question! Here's how I'd think about it: [Insert clever reasoning here for: '{user_input}']"
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response))

# Full Mode behavior
else:
    st.warning("⚠️ You're in Full Mode. Make sure Ollama is installed and running locally.")
    if user_input:
        try:
            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": user_input},
                timeout=10
            )
            ollama_response.raise_for_status()
            raw_output = ollama_response.json()
            response = raw_output.get("response", "🤖 No response from Ollama.")
        except Exception as e:
            response = f"❌ Could not connect to Ollama.\n\n{e}"
        
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response))

# Display chat history
if st.session_state.chat_history:
    st.markdown("### 🧠 Chat History")
    for role, msg in st.session_state.chat_history:
        st.markdown(f"**{role}:** {msg}")

# Footer
st.markdown("---")
st.markdown("🔁 _Switch between Demo Mode and Full Mode using the toggle above._")

