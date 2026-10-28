from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from dotenv import load_dotenv
from typing import TypedDict, Annotated


load_dotenv()
model = ChatGroq(model = "qwen/qwen3.8-27b")


# state
class ChatState(TypedDict):
    
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    
    messages = state["messages"]
    response = model.invoke(messages)
    
    return {"messages": [response]}

# graph
graph = StateGraph(ChatState)
checkpointer = MemorySaver()

# nodes
graph.add_node("chat_node", chat_node)

# edges
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)



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


# thread_id = "1"

# while True:
    
#     user_input = input("You: ")
#     print("You: ", user_input)
    
#     if user_input.strip().lower() in ["exit", "quit", "bye"]:
#         break
    
#     config = {"configurable": {"thread_id": thread_id}}
#     response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    
#     print("AI: ", response["messages"][-1].content)