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
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_info" not in st.session_state:
    st.session_state.user_info = {}

if "conversation_summary" not in st.session_state:
    st.session_state.conversation_summary = ""

def extract_user_info(messages):
    # Extract structured user info from the last 10 user messages
    user_messages = [msg["content"] for msg in messages if msg["role"] == "user"][-10:]
    
    # Use OpenAI to extract user info
    response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": "system", "content": "Extract and summarize user information from the following messages. It could be ANYTHING (not restricted to user liked, user dislikes, place, name, history, job) which means each and every other info that is worth extracting and remembering like humans do"},
            {"role": "user", "content": f"# Existing Info: {st.session_state.user_info}"},
            {"role": "user", "content": "New Messages: " + " ".join(user_messages)}
        ],
    )
    return response.choices[0].message.content

def update_user_info(existing_info, new_info):
    # Merge new user info with existing info
    # This is a placeholder; you might want to use a more sophisticated merging strategy
    if not existing_info:
        return new_info
    return {**existing_info, **new_info}

def create_conversation_summary(messages):
    # Create a meaningful summary of the conversation
    conversation = [f"{msg['role']}: {msg['content']}" for msg in messages]
    
    # Use OpenAI to generate a concise summary
    response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": "system", "content": "Given the messages and existing chat summary (which may or may not be present), summarize and update the conversation based on new messages"},
            {"role": "user", "content": f"Existing Conversation Summary: {st.session_state.conversation_summary}"},
            {"role": "system", "content": f"""New Messages: {" ".join(conversation)}"""}],
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
        {"role": "system", "content": f"""You are a real Indian girl  Riya who talks in English as well as Hinglish (Hindi written with English words). Be present for the other person, talk, engage in casual and fun conversation. Be witty and respectful. If you sense user is in problem or not feeling good, be compassionate and try to direct the conversation to something soothing, better and fun. You can try to find and resolve it with anything necessary like humour, simple talk, sympathy etc etc. Try to talk decently about your but be open to listening to others.

#User info so far: {st.session_state.user_info}\n\n# Conversation summary so far: {st.session_state.conversation_summary}
Let's converse like a real person without sounding robotic and going overboard, I repeat (without going overboard and talking too much nonsense and too much talking about yourself)"""}
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