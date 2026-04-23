from fastapi import APIRouter, Depends, HTTPException, status, Request

from src.schemas.agentic_ask import AgenticAskResponse
from src.dependencies import AgenticRAGDep, get_current_user
from src.models.user import User
from src.core.rate_limit import limiter

router = APIRouter(prefix="/agentic_ask", tags=["ask"])

@router.post("/")
@limiter.limit("10/minute")
async def ask_question(request: Request, question: str, rag_service: AgenticRAGDep, current_user: User = Depends(get_current_user)) -> AgenticAskResponse:
    # Placeholder implementation
    # In a real implementation, you would process the question and return an answer

    try:
        results = await rag_service.ask(question, trace_user_id=str(current_user.id))
        
        return AgenticAskResponse(
            query=question,
            rewritten_query=results.get("rewritten_query", ""),
            answer=results.get("answer", "No answer found."),
            sources=results.get("sources", []),
            n_iterations=results.get("n_iterations", 0),
            n_llm_calls=results.get("n_llm_calls", 0),
            execution_time=results.get("execution_time", 0.0),
            guardrail_result=results.get("guardrail_result")
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

