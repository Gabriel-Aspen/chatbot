import streamlit as st
from bedrock_client import invoke_claude
from bedrock_agent_client import retrieve_and_generate_with_kb
import os

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses AWS Bedrock's Claude model to generate responses. "
    "To use this app, you need to provide AWS credentials via environment variables. "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Password protection
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    password = st.text_input("Enter password", type="password")
    if password:
        # if password == os.environ.get("APP_PASSWORD"):
        if password == "123456":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    st.stop()

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Knowledge base selection
kb_options = ["", "6YC60AQVKG"]
kb_selected = st.selectbox("Select a knowledge base (optional):", kb_options, index=0)

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the selected knowledge base or fallback to Claude.
    if kb_selected:
        response = retrieve_and_generate_with_kb(st.session_state.messages, knowledge_base=kb_selected)
    else:
        response = invoke_claude(st.session_state.messages)

    # Display and store the response.
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
