import os
import streamlit as st

from st_chat_message import message, message_stream

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore


st.set_page_config(page_title="st-chat-message: OpenAI Streaming", page_icon="🤖")

api_key = os.getenv("OPENAI_API_KEY", "")
model = st.sidebar.text_input("OpenAI Chat Model", value="gpt-4o-mini")
temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)

if not api_key:
    st.info("Set OPENAI_API_KEY in your environment to run this demo.")

if "chat" not in st.session_state:
    st.session_state.chat = []  # list[dict(role, content)]

prompt = st.text_input("Message", value="Stream a short assistant response.")

if st.button("Send") and prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})

for i, msg in enumerate(st.session_state.chat):
    message(msg["content"], is_user=(msg["role"] == "user"), key=f"cmsg_{i}")

if st.session_state.chat and st.session_state.chat[-1]["role"] == "user" and api_key and OpenAI is not None:
    client = OpenAI(api_key=api_key)

    # Construct messages history for context
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.chat
    ]

    # Call the Chat Completions API with streaming enabled
    stream = client.chat.completions.create(
        model=model,
        messages=history,
        temperature=temperature,
        stream=True,
    )

    def text_deltas():
        for event in stream:
            # OpenAI Python SDK v1: choices[].delta.content contains text fragments
            for choice in getattr(event, "choices", []) or []:
                delta = getattr(choice, "delta", None)
                if not delta:
                    continue
                content = getattr(delta, "content", None)
                if content:
                    yield content

    final = message_stream(
        text_deltas(),
        is_user=False,
        key="openai_stream",
        rich_content=True,
        throttle_ms=20,
        flush_every=1,
    )

    st.session_state.chat.append({"role": "assistant", "content": final})