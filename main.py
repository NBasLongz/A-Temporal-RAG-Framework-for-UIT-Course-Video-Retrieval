import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.users import router as users_router
from src.api.videos import router as videos_router
from src.api.chunks import router as chunks_router
from src.api.agentic_ask import router as agentic_ask_router
from src.api.auth import router as auth_router

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import engine
from src.models.base import Base
from src.database.seed import seed_db_if_empty, seed_vector_db_if_empty

from src.services.rag.bm25 import make_bm25_retriever
from src.services.rag.vectordb import make_vector_db_retriever
from src.services.rag.factory import make_agentic_rag_service
from src.core.config import get_settings
from src.core.rate_limit import limiter


from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

from src.core.logging import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Settings setup
    logger.info("Loading application settings...")
    settings = get_settings()
    app.state.settings = settings
    logger.info("Application settings loaded and stored in app state.")


    # This runs when the server starts
    max_retries = 3
    retry_delay = 5
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                # Create all tables defined in your models
                await conn.run_sync(Base.metadata.create_all)
            
            async with AsyncSession(engine) as session:
                # Optionally seed the database with initial data if it's empty
                await seed_db_if_empty(session)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to the database after {max_retries} attempts.")
                raise e
 
    await seed_vector_db_if_empty() # Async func

    # Create and store the BM25 retriever in the app state for later use
    logging.info("Initializing BM25 retriever...")
    bm25_retriever = make_bm25_retriever()
    app.state.bm25_retriever = bm25_retriever
    logging.info("Initialized BM25 retriever and stored in app state.")

    # Create and store the Chroma retriever in the app state for later use
    logging.info("Initializing Chroma retriever...")
    chroma_retriever = make_vector_db_retriever()
    app.state.chroma_retriever = chroma_retriever
    logging.info("Initialized Chroma retriever and stored in app state.")

    #Create and store Agentic Rag Service in the app state for later use
    logging.info("Initializing Agentic RƯAG service...")
    rag_service = make_agentic_rag_service(
            bm25_retriever,
            chroma_retriever,
            retriever_top_k=settings.retriever_top_k,
            reranker_top_k=settings.reranker_top_k,
        )
    app.state.rag_service = rag_service
    logging.info("Initialized Agentic RAG service and stored in app state.")

    # Crate and store the Limiter in the app state for later use
    logging.info("Initializing rate limiter...")
    app.state.limiter = limiter

    yield

app = FastAPI(lifespan=lifespan)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(videos_router)
app.include_router(chunks_router)
app.include_router(agentic_ask_router)

app.mount("/media", StaticFiles(directory="/app/media"), name="media")
app.mount("/", StaticFiles(directory="/app/public", html=True), name="public")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)