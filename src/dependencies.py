from typing import Annotated

from src.database.session import async_session_maker
from src.services.user import UserService
from src.services.video import VideoService
from src.services.chunk import ChunkService
from src.services.rag.agent_graph import AgenticRagService

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.retrievers import BM25Retriever
from langchain_core.vectorstores import VectorStoreRetriever

from fastapi import Depends, HTTPException, Request

import logging
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from src.core.security import ALGORITHM, SECRET_KEY
from src.schemas.user import TokenData
from src.models.user import User

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/token")

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_user_service(dependency_session: AsyncSession = Depends(get_db_session)):
    return UserService(dependency_session)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        token_data = TokenData(email=email)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_service.get_user_by_email(email=token_data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

    logger.info("Creating UserService with provided database session.")
    return UserService(dependency_session)

def get_video_service(dependency_session: AsyncSession = Depends(get_db_session)):
    return VideoService(dependency_session)

def get_chunk_service(dependency_session: AsyncSession = Depends(get_db_session)):
    return ChunkService(dependency_session)

def get_vector_db_retriever(request: Request) -> VectorStoreRetriever:
    retriever = getattr(request.app.state, "chroma_retriever", None)
    if not retriever:
        # Prevent errors if queried before data exists
        raise HTTPException(
            status_code=503,
            detail="Vector database is not yet initialized."
        )
    return retriever

def get_bm25_retriever(request: Request) -> BM25Retriever:
    retriever = getattr(request.app.state, "bm25_retriever", None)
    if not retriever:
        # Prevent errors if queried before data exists
        raise HTTPException(
            status_code=503, 
            detail="BM25 Search index is not yet built or the database is empty."
        )
    return retriever

def get_agentic_rag_service(request: Request) -> AgenticRagService:
    rag_service = getattr(request.app.state, "rag_service", None)
    if not rag_service:
        # Prevent errors if queried before data exists
        raise HTTPException(
            status_code=503, 
            detail="RAG service is not yet initialized."
        )
    return rag_service

AgenticRAGDep = Annotated[AgenticRagService, Depends(get_agentic_rag_service)]
VideoServiceDep = Annotated[VideoService, Depends(get_video_service)]