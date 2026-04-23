from src.services.rag.nodes.utils import extract_sources_from_tool_messages
from src.services.rag.tools import create_retriever_tool
from .nodes import (
    continue_after_guardrail,
    invoke_query_guardrail,
    invoke_out_of_scope_response,
    invoke_query_rewrite,
    invoke_get_relevant_documents,
    invoke_rerank,
    invoke_generate_answer,
    invoke_grade_answer,
    invoke_response
)
from src.services.rag.config import GraphConfig
from src.services.rag.state import ThreadState
from src.services.rag.context import Context

from langchain_community.retrievers import BM25Retriever
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from langfuse.langchain import CallbackHandler
from langfuse import get_client, propagate_attributes

from langgraph.prebuilt import tools_condition, ToolNode
from collections.abc import AsyncGenerator
from typing import Optional
import uuid
import time
import logging

logger = logging.getLogger(__name__)

class AgenticRagService:
    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        vectordb_retriever: VectorStoreRetriever,
        graph_config: Optional[GraphConfig] = None
    ):
        self.bm25_retriever = bm25_retriever
        self.vectordb_retriever = vectordb_retriever
        self.graph_config = graph_config or GraphConfig()

        self.graph = self._build_graph()

    def _build_graph(self):
        # Build the graph using the provided nodes and configuration
        logger.info("Building the agentic RAG graph!")

        hybrid_search = create_retriever_tool(
            vectordb_retriever=self.vectordb_retriever,
            bm25_retriever=self.bm25_retriever,
            top_k=self.graph_config.retriever_top_k,
            use_hybrid=self.graph_config.use_hybrid,
            semantic_weight=self.graph_config.semantic_weight,
            bm25_weight=self.graph_config.bm25_weight
        )
        tools = [hybrid_search]

        workflow = StateGraph(ThreadState, context_schema=Context)
        workflow.add_node("query_guardrail", invoke_query_guardrail)
        workflow.add_node("out_of_scope_response", invoke_out_of_scope_response)
        workflow.add_node("query_rewrite", invoke_query_rewrite)
        workflow.add_node("get_relevant_documents", invoke_get_relevant_documents)
        workflow.add_node("search_tool", ToolNode(tools))
        workflow.add_node("rerank", invoke_rerank)
        workflow.add_node("generate_answer", invoke_generate_answer)
        # workflow.add_node("grade_answer", invoke_grade_answer)
        workflow.add_node("response", invoke_response)

        workflow.set_entry_point("query_guardrail")

        workflow.add_conditional_edges(
            "query_guardrail",
            continue_after_guardrail,
            {"continue": "query_rewrite", "out_of_scope": "out_of_scope_response"}
        )

        workflow.add_edge("out_of_scope_response", END)
        workflow.add_edge("query_rewrite", "get_relevant_documents")

        workflow.add_conditional_edges(
            "get_relevant_documents",
            tools_condition,
            {"tools": "search_tool"}
        )
        workflow.add_edge("search_tool", "rerank")
        workflow.add_edge("rerank", "generate_answer")
        workflow.add_edge("generate_answer", "response")

        # workflow.add_conditional_edges(
        #     "grade_answer",
        #     lambda state: state.get("routing_decision", "response"),
        #     {"response": "response", "rewrite_query": "query_rewrite"}
        # )

        workflow.add_edge("response", END)

        logger.info("Compiling the graph...")
        completed_graph = workflow.compile()
        logger.info("Graph compilation completed!")

        return completed_graph

    async def ask(
        self,
        query: str,
        model: Optional[str] = None,
        trace_user_id: Optional[str] = None,
    ) -> dict:
        # Main method to handle user query and return answer
        return await self._execute_graph(query, model, trace_user_id)

    async def _execute_graph(self, query: str, model: Optional[str], trace_user_id: Optional[str] = None) -> dict:
        start_time = time.time()

        logger.info("Invoking LangGraph workflow")

        model_to_use = model or self.graph_config.llm_model

        logger.info("Initialze state")
        inital_state = {
            "messages": [HumanMessage(content=query)],
            "n_iterations": 0,
            "n_llm_calls": 0,
            "original_query": None,
            "rewritten_query": [],
            "guardrail_result": None,
            "sources": [],
            "answer": None,
            "answer_grade": [],
            "routing_decision": None
        }

        logger.info("Initialze runtime context")
        runtime_context = Context(
          llm_model = model_to_use,
          model_provider = "google-genai",
          temperature = self.graph_config.temperature,
          retriever_top_k = self.graph_config.retriever_top_k,
          reranker_top_k = self.graph_config.reranker_top_k,
          n_iterations = self.graph_config.n_iterations
        )
        
        handler = CallbackHandler()
        langfuse = get_client()
        user_id_for_trace = trace_user_id or "anonymous"

        with langfuse.start_as_current_observation(as_type="span", name="langchain-call"):
            # Propagate session_id to all observations
            with propagate_attributes(session_id=str(uuid.uuid4()), user_id=user_id_for_trace):

                result = await self.graph.ainvoke(
                                    inital_state,
                                    context=runtime_context,
                                    config = {
                                        "callbacks": [handler]
                                    }
                                )

        execution_time = time.time() - start_time
        logger.info(f"Graph execution completed in {execution_time:.2f}s")

        # Extract last results
        answer = self._extract_answer(result)
        sources = self._extract_sources(result)
        n_iterations = result.get("n_iterations", 0)
        n_llm_calls = result.get("n_llm_calls", 0)
        rewritten_query = result.get("rewritten_query", [])[-1] if result.get("rewritten_query") else ""
        guardrail_result = result.get("guardrail_result").reasoning if result.get("guardrail_result") else ""

        return {
            "query": query,
            "rewritten_query": rewritten_query,
            "answer": answer,
            "sources": sources,
            "n_iterations": n_iterations,
            "n_llm_calls": n_llm_calls,
            "execution_time": execution_time,
            "guardrail_result": guardrail_result
        }

    async def ask_streaming(self, query: str, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Stream the final answer for a query in fixed-size text chunks.

        The current graph produces the answer as a complete response, so this
        method awaits the graph execution first and then yields the answer in
        order-preserving chunks. This keeps the public API streaming-friendly
        without changing the graph nodes yet.
        """
        result = await self._execute_graph(query, model)

        answer = result.get("answer", "")
        if not answer:
            return

        chunk_size = 256
        for start in range(0, len(answer), chunk_size):
            yield answer[start : start + chunk_size]

    def _extract_answer(self, result: dict) -> str:
        messages = result.get("messages", [])

        if not messages:
            return "No answer generated"

        last_message = messages[-1]
        return last_message.content if hasattr(last_message, "content") else str(last_message)

    def _extract_sources(self, result: dict) -> list:
        return result.get("sources", [])

    def _extract_reasoning(self, result: dict) -> str:
        return

    def get_graph_visualization(self) -> bytes:
      """Get the LangGraph workflow visualization as PNG.
      """
      try:
          logger.info("Generating graph visualization as PNG")
          png_bytes = self.graph.get_graph().draw_mermaid_png()
          logger.info(f"Generated PNG visualization ({len(png_bytes)} bytes)")
          return png_bytes
      except ImportError as e:
          logger.error(f"Failed to generate visualization - missing dependencies: {e}")
          logger.error("Install with: pip install pygraphviz or apt-get install graphviz")
          raise ImportError(
              "Graph visualization requires pygraphviz. "
              "Install with: pip install pygraphviz (requires graphviz system package)"
          ) from e
      except Exception as e:
          logger.error(f"Failed to generate graph visualization: {e}")
          raise