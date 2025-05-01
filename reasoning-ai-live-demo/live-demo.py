import streamlit as st
import time

# Function to simulate the typing animation using a placeholder
def typewriter_effect(text, speed=0.01):
    placeholder = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(f"```markdown\n{displayed_text}\n```")
        time.sleep(speed)

# Page title
st.set_page_config(page_title="Reasoning AI Chatbot", page_icon="🤖")
st.title("🧠 Reasoning AI Assistant")
st.caption("Ask any Python-related question. The AI will explain and then code.")

# Static question and response
question = "write a simple print statement"
response = """
<think> Okay, so I need to write a simple print statement in Python. Let me think about how to do that.
First, I remember that printing is done using the print() function. So I should start by calling print followed by an argument inside parentheses.

What type of argument should I use? Since it's a simple example, maybe just a number or a string would work. Let me pick a number first.

So the code should look like print(5). That way, when I run this line, it will output 5 on the screen.

Wait, but sometimes people might want to see a message instead of a number. Like print("Hello World"). But for a simple case, maybe just using a number is enough and easier to understand.

Let me test this in my mind. If I type print(5), does it display 5? Yes, that's correct.

Is there anything else I need to consider? Maybe using different data types like strings or booleans could be explored later, but for now, sticking to a number should suffice.

So putting it all together, the code will be:

print(5)

I think that's straightforward. It's clear and meets the requirement of writing a simple print statement. </think>

**Reasoning**: To print a number in Python, use the `print()` function with an integer or string as the argument inside parentheses.

**Code**:
```python
print(5)
