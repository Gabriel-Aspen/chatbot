import streamlit as st
from bedrock_client import invoke_claude
from bedrock_agent_client import retrieve_and_generate_with_kb

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

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the Bedrock Claude model.
    response = retrieve_and_generate_with_kb(st.session_state.messages)

    # Display and store the response.
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
