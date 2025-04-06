import streamlit as st
import ollama

st.set_page_config(page_title="Reasoning AI Chatbot", layout="centered")
st.title("🧠 Reasoning AI Assistant")
st.caption("Ask any Python-related question. The AI will explain and then code.")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "For each question, provide an explanation first, followed by the Python code example. Format the response as:\n\n**Reasoning:**\n[Explanation]\n\n**Code:**\n```python\n[Python Code]\n```"}
    ]

# User input
user_input = st.text_input("Enter your message:", key="user_input")
if st.button("Submit") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        response = ollama.chat(model="deepseek-r1:1.5b", messages=st.session_state.messages)
        assistant_msg = response.get("message", {}).get("content", "No response received.")
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
    except Exception as e:
        assistant_msg = f"Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})

# Display chat history
for msg in st.session_state.messages[1:]:  # Skip system prompt
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(msg["content"])
