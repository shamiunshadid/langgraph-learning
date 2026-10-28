import streamlit as st
from chatbot_backend_with_db import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid


# utility functions
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def new_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)
        
def load_chat(thread_id):
    return chatbot.get_state(config={"configurable": {"thread_id": thread_id}}).values["messages"]



if "message_history" not in st.session_state:
    st.session_state["message_history"] = []
    
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()
    
if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()


add_thread(st.session_state["thread_id"])


# sidebar ui
st.sidebar.title("Chatbot")

if st.sidebar.button("New chat"):
    new_chat()

st.sidebar.header("All chats")

for thread_id in st.session_state["chat_threads"][::-1]:
    if st.sidebar.button(str(thread_id)):
        # after button click logic
        st.session_state["thread_id"]= thread_id
        messages = load_chat(thread_id)
        
        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = "ai"
            temp_messages.append({"role": role, "content": msg.content})
            
        st.session_state["message_history"] = temp_messages




for messages in st.session_state["message_history"]:
    with st.chat_message(messages["role"]):
        st.text(messages["content"])


user_input = st.chat_input()

config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

if user_input:
    
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)
    

    with st.chat_message("ai"):
        
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]}, 
                config=config,
                stream_mode="messages"
            )
        )
    st.session_state["message_history"].append({"role": "ai", "content": ai_message})

