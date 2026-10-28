from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
# from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from dotenv import load_dotenv
from typing import TypedDict, Annotated
import sqlite3

load_dotenv()
model = ChatGroq(model = "qwen/qwen3.8-27b")


# state
class ChatState(TypedDict):
    
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    
    messages = state["messages"]
    response = model.invoke(messages)
    
    return {"messages": [response]}



connection = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=connection)


# graph
graph = StateGraph(ChatState)

# nodes
graph.add_node("chat_node", chat_node)

# edges
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# getting all threads from sqlite db
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    
    return list(all_threads)


def summarize_chat_title(user_message: str) -> str:
    response = model.invoke([
        SystemMessage(
            content=(
                "Create a concise sidebar title for this chat, "
                "about 2-6 words. Return only the title."
            )
        ),
        HumanMessage(content=user_message),
    ])
    return response.content.strip().strip('"')