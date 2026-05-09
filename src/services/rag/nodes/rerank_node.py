from src.services.rag.nodes.utils import (
    extract_sources_from_tool_messages,
    get_latest_query
)
from src.services.rag.state import ThreadState
from src.services.rag.context import Context

from langgraph.runtime import Runtime
from langchain_core.documents import Document
from typing import Dict, List
import httpx
import logging

logger = logging.getLogger(__name__)


async def _call_reranker(
    reranker_url: str,
    query: str,
    docs: List[Document],
    top_k: int,
) -> List[Document]:
    """Call the inference service and return the top-k re-ranked Documents."""

    passages = [d.page_content for d in docs]

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{reranker_url}/rerank",
            json={"query": query, "passages": passages},
        )
        response.raise_for_status()

    results = response.json()["results"]  # [{passage, score}, ...]

    # Map scored passages back to original Document objects (preserving metadata)
    passage_to_doc: Dict[str, Document] = {d.page_content: d for d in docs}

    reranked_docs: List[Document] = []
    for item in results[:top_k]:
        doc = passage_to_doc.get(item["passage"])
        if doc is not None:
            reranked_docs.append(doc)

    return reranked_docs


async def invoke_rerank(state: ThreadState, runtime: Runtime[Context]) -> Dict:
    logger.info("NODE: rerank")

    ctx = runtime.context
    query = state.get("original_query") or get_latest_query(state.get("messages", []))
    docs = extract_sources_from_tool_messages(state.get("messages", []))

    if not docs:
        logger.warning("rerank node received no documents – skipping.")
        return {"sources": []}

    logger.info(
        f"Reranking {len(docs)} docs → top {ctx.reranker_top_k} "
        f"via {ctx.reranker_url}"
    )

    try:
        reranked = await _call_reranker(
            reranker_url=ctx.reranker_url,
            query=query,
            docs=docs,
            top_k=ctx.reranker_top_k,
        )
        logger.info(f"Reranking complete – kept {len(reranked)} docs.")
        return {"sources": reranked}

    except httpx.HTTPError as exc:
        # Graceful degradation: if the reranker is down, pass all docs through
        logger.error(f"Reranker service unreachable ({exc}). Returning all docs unranked.")
        return {"sources": docs[: ctx.reranker_top_k]}