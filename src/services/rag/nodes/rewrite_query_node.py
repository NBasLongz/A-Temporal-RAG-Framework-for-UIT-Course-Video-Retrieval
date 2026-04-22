from src.services.rag.state import (
    ThreadState
)
from src.services.rag.context import Context
from src.services.rag.prompts import (
    query_rewrite_prompt,
)
from .utils import get_latest_query

from langgraph.runtime import Runtime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

async def invoke_query_rewrite(state: ThreadState, runtime: Runtime[Context]) -> Dict:
    logger.info("NODE: query_rewrite")
    query = state.get("original_query")
    
    prompt = query_rewrite_prompt.format(
        query=query,
    )
    
    llm = ChatGoogleGenerativeAI(model=runtime.context.llm_model, temperature=runtime.context.temperature)
    res = await llm.ainvoke(prompt)
    return {
        "messages": [HumanMessage(content=res.content)],
        "rewritten_query": [res.content],
        "n_llm_calls": state.get("n_llm_calls", 0) + 1
    }