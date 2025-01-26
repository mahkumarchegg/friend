from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone")

# Get API key from user input
api_key = st.text_input("Enter your OpenAI API key", type="password")

if not api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

client = OpenAI(api_key=api_key)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_info" not in st.session_state:
    st.session_state.user_info = {"likes": [], "dislikes": [], "other": []}

if "conversation_summary" not in st.session_state:
    st.session_state.conversation_summary = ""

def extract_user_info(messages):
    # Extract structured user info from the last 10 user messages
    user_messages = [msg["content"] for msg in messages if msg["role"] == "user"][-10:]
    # Example logic: Extract likes, dislikes, and other info
    new_info = {"likes": [], "dislikes": [], "other": []}
    for msg in user_messages:
        if "like" in msg.lower():
            new_info["likes"].append(msg)
        elif "dislike" in msg.lower():
            new_info["dislikes"].append(msg)
        else:
            new_info["other"].append(msg)
    return new_info

def update_user_info(existing_info, new_info):
    # Merge new user info with existing info
    for key in existing_info:
        existing_info[key].extend(new_info[key])
    return existing_info

def create_conversation_summary(messages):
    # Create a meaningful summary of the conversation
    conversation = [f"{msg['role']}: {msg['content']}" for msg in messages]
    summary = " ".join(conversation)
    # Example: Use OpenAI to generate a concise summary
    response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[{"role": "system", "content": f"Summarize the following conversation in one sentence: {summary}"}],
    )
    return response.choices[0].message.content

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if we need to extract user info or create a new summary
    user_message_count = sum(1 for msg in st.session_state.messages if msg["role"] == "user")
    if user_message_count % 10 == 0:
        new_user_info = extract_user_info(st.session_state.messages)
        st.session_state.user_info = update_user_info(st.session_state.user_info, new_user_info)
        st.session_state.conversation_summary = create_conversation_summary(st.session_state.messages)

    # Prepare the messages for the API call
    messages_for_api = [
        {"role": "system", "content": f"You are a helpful assistant. Use the following user info and conversation summary to provide personalized responses. User info: {st.session_state.user_info}. Conversation summary: {st.session_state.conversation_summary}"}
    ]
    # Add the last 20 messages (10 from each side)
    recent_messages = st.session_state.messages[-20:]
    messages_for_api.extend(recent_messages)

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=messages_for_api,
                stream=True,
            )
            response = st.write_stream(stream)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Pop the oldest message if the list exceeds 50 messages
    if len(st.session_state.messages) > 50:
        st.session_state.messages.pop(0)