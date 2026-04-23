from typing import List
from langchain import messages
from langchain.messages import HumanMessage, AIMessage, ToolMessage, AnyMessage
from langchain_core.documents import Document

def extract_sources_from_tool_messages(messages: List) -> List[Document]:
    """Extract sources from tool messages in conversation.

    :param messages: List of messages from graph state
    :returns: List of SourceItem objects
    """
    sources = []
    
    for msg in messages:
        if isinstance(msg, ToolMessage) and hasattr(msg, "name"):
            if msg.name == "hybrid_search":
                sources = eval(msg.content, {"Document": Document})
    
    return sources


def get_latest_query(messages: List) -> str:
    """Get the latest user query from messages.

    :param messages: List of messages
    :returns: Latest query text
    :raises ValueError: If no user query found
    """
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content

    raise ValueError("No user query found in messages")


def get_latest_context(messages: List) -> List[Document]:
    """Get the latest context from tool messages.

    :param messages: List of messages
    :returns: Latest context text or empty string
    """
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            return msg.content if hasattr(msg, "content") else []

    return []

def format_context(documents: List[Document]) -> str:
    """Build context string from tool messages.

    :param messages: List of messages
    :returns: Concatenated context string from tool messages
    """
    context = ""

    for res in documents:
        context += "---\n"
        context += f"Video: {res.metadata.get('video_name')}\n"
        context += f"Timestamp: {res.metadata.get('timestamp')}\n"
        context += f"{res.page_content}\n"
    return context

def filter_messages(messages: List, n: int = None) -> List[HumanMessage | AIMessage]:
    """Filter messages to keep only the latest n messages of Human or AI.

    :param messages: List of messages
    :param n: Number of latest messages to keep
    :returns: Filtered list of messages
    """
    if n is None:
        return [msg for msg in reversed(messages) if isinstance(msg, (HumanMessage, AIMessage))]
    
    return [msg for msg in reversed(messages) if isinstance(msg, (HumanMessage, AIMessage))][:n]

def trim_messages(messages: List, n: int = 10) -> List[AnyMessage]:
    """Trim messages to keep only the latest n messages.

    :param messages: List of messages
    :param n: Number of latest messages to keep
    :returns: Trimmed list of messages
    """
    return messages[-n:]