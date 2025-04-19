import streamlit as st
import openai

# Page config
st.set_page_config(page_title="Reasoning AI Chatbot", layout="centered")
st.title("🧠 Reasoning AI Assistant")
st.caption("Ask any Python-related question. The AI will explain and then code.")

# Load API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that explains Python programming concepts "
                "and writes clean, readable code.\n\n"
                "Respond with the following format:\n\n"
                "**Reasoning:**\n[Explanation]\n\n**Code:**\n```python\n[Python Code]\n```"
            ),
        }
    ]

# User input
user_input = st.text_input("Enter your message:")
if st.button("Submit") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages,
            temperature=0.7
        )
        assistant_msg = response.choices[0].message["content"]
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
    except Exception as e:
        assistant_msg = f"❌ Error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})

# Display chat history
for msg in st.session_state.messages[1:]:  # Skip system prompt
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(msg["content"])
