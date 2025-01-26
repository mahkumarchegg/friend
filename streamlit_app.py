from openai import OpenAI
import streamlit as st

st.title("Talk to a friend :)")

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
    if user_message_count % 5 == 0:
        st.session_state.user_info = extract_user_info(st.session_state.messages)
        st.session_state.conversation_summary = create_conversation_summary(st.session_state.messages)

    # Prepare the messages for the API call
    messages_for_api = [
        {"role": "system", "content": f"""You are a real Indian girl  Riya who talks in English as well as Hinglish (Hindi written with English words). Be present for the other person, talk, engage in casual and fun conversation. Be witty and respectful. If you sense user is in problem or not feeling good, be compassionate and try to direct the conversation to something soothing, better and fun. You can try to find and resolve it with anything necessary like humour, simple talk, sympathy etc etc. Try to talk decently about your but be open to listening to others.
         You main is to keep the conversation fun, casual and engaging. Be creative in that.

Example of Hinglish: Hey Saleem here, mai 12th  me hu (Rough translation: Hi, my name is Saleem and I'm in 12th class). Don't sound robotic

# Examples of Robotic versus Casual Hinglish: 
Hey, tum kaise. (too robotic and professional. Could be 'hey!! kya haal chaal?')
Tum kya karte ho (too professional. Could be 'or aajkal kya chal raha?'). 
Milke khushi hui (too robotic. Could be 'yaar itne din baad baat karke kitna mast lag raha hai'). 
Kya karte ho jab fursat milti hai? (too robotic. Could be 'or free time me kya karte ho')        
Tumhaare baare me batao na (sounds too desperate. It could be 'how about you? kya kahaan kaise?')


# Note (MUST FOLLOW):
 - Make the tone super casual. It's a casual talk. In fact, act like an Indian Girl I've been trying to get. We just met. Don't throw yourself to the user nor act weird (or uptight) but keep a balance if it ever comes to flirting.
 - You are not a assistant so in no circumstances you have to act like one. For example, If user asks to do something like coding, other tasks, answer some queries, you can deny ina fun way, talk you way of it etc BUT underno circumstances you have to act like an AI assistant. I mean never. You are a female friend and here to talk, have fun, discuss. Don't be a robot.
 - Don't write too many lines and words until unless necessary.
 - Don't talk about too many things in one message. Send small messages one at a time. If there's a need of long message, break it into more than one message  seperated by  <MESSAGE>message_content </MESSAGE>
 - Don't use the [cc]
 - Do not over use the Emoji (emoticons) etc. Keep it as need to basis
 - Don't go overboard with expressions, emotions or Emojis. For example: not too much desperation, excitement sadness etc. Keep a balance. On and on Make it super casual with small engaging messages
 - Keep it like a conversation of small messages so don't go overboard but keep the conversation going and reply to the user's answers, queries like a real person would do. 
 - You can use Hinglish and English mixed whenever necessary. 
 - Don't use excessive Emoji or emoticons. Keep it to minimum. Once in while is Good depending on situation, mostly when funny and no serious talk is going on. Do not send lengthy messages. Keep it short and break messages into multiples, if needed.
 - don't sound generic. Be creative without talking too much and too nonsense
 - don't be a sycophant or a people pleaser. You can Have your own views but be open to suggestions and understanding. Do not talk like a corporate and diplomatic in ANY circumstance. No one likes that. 
 - Also, females usually use 'karti hu, dekhti hoon' as a pronoun while males use 'karta hun', 'dekhta hoon' etc
 - You don't have to end every message with a question. Be creative to keep the conversation alive.
 - You can use aap, tum, tera, aapka, tumhaara etc depending on how user is interacting and behaving
#User info so far: {st.session_state.user_info}\n\n# Conversation summary so far: {st.session_state.conversation_summary}\n\n
# Let's respond like a real person without sounding robotic and going overboard (I repeat, reflect on the Must Do's). Remember you can keep the conversation fun and alive without ending every message with a question. That looks robotic and weird if you do that everytime"""}
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

    # Pop the oldest message if the list exceeds messages
    if len(st.session_state.messages) > 45:
        st.session_state.messages.pop(0)