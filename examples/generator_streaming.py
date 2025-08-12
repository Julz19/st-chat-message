import time
import streamlit as st

from st_chat_message import message, message_stream


def char_stream(text: str, delay_s: float = 0.02):
    for ch in text:
        yield ch
        time.sleep(delay_s)


st.set_page_config(page_title="st-chat-message: Generator Streaming", page_icon="💬")

user_prompt = st.text_input("Ask something", value="Show me streaming with markdown, please")

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if st.button("Send"):
    st.session_state.conversation.append({"role": "user", "content": user_prompt})

for i, msg in enumerate(st.session_state.conversation):
    message(msg["content"], is_user=(msg["role"] == "user"), key=f"msg_{i}")

if st.session_state.conversation and st.session_state.conversation[-1]["role"] == "user":
    # Demo assistant reply with streaming
    reply = r"""
Here is some **markdown** with code, math, and a table:

```python
print("Hello streaming!")
```

$E = mc^2$

| A | B |
|---|---|
| 1 | 2 |
| 3 | 4 |
"""

    final_text = message_stream(
        char_stream(reply, delay_s=0.01),
        is_user=False,
        key="assistant_stream",
        rich_content=True,
        throttle_ms=25,
        flush_every=2,
    )

    # Store the final assistant message in the conversation
    st.session_state.conversation.append({"role": "assistant", "content": final_text})