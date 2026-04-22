import csv
import os
import pickle
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, select, text

from src.models.video import Video
from src.models.chunk import Chunk

from langchain_chroma import Chroma
import logging

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


async def ensure_user_schema(session: AsyncSession):
    async with session.bind.begin() as conn:
        def _migrate(sync_conn):
            inspector = inspect(sync_conn)
            if not inspector.has_table("users"):
                return

            existing_columns = {column["name"] for column in inspector.get_columns("users")}
            if "hashed_password" not in existing_columns:
                sync_conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255) NOT NULL DEFAULT ''"
                    )
                )

        await conn.run_sync(_migrate)

async def seed_db_if_empty(session: AsyncSession):
    # Check if there's any data already
    result = await session.execute(select(Video).limit(1))
    if result.scalars().first() is not None:
        logger.info("Database already has data, skipping seeding.")
        return

    # 1. Load Videos
    videos = {} # Store by video_uuid to look up later
    with open(os.path.join(DATA_DIR, "videos.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vid_id = uuid.UUID(row["video_uuid"])
            video = Video(
                id=vid_id,
                name=row["video_name"],
                url=row["video_url"]
            )
            session.add(video)
            videos[vid_id] = video

    # 2. Load Chunks
    chunks = {} # Store by chunk_uuid
    with open(os.path.join(DATA_DIR, "chunks.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            chunk_id = uuid.UUID(row["chunk_uuid"])
            
            try:
                timestamp = int(float(row["timestamp"])) if row["timestamp"] else 0
            except ValueError:
                timestamp = 0
                
            try:
                duration = int(float(row["duration"])) if row["duration"] else 0
            except ValueError:
                duration = 0

            chunk = Chunk(
                id=chunk_id,
                content=row["content"],
                timestamp=timestamp,
                duration=duration
                # video_id will be mapped next
            )
            chunks[chunk_id] = chunk

    # 3. Map video_id to chunks using video_chunks.csv
    with open(os.path.join(DATA_DIR, "video_chunks.csv"), mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vid_id = uuid.UUID(row["video_uuid"])
            chunk_id = uuid.UUID(row["chunk_uuid"])
            if chunk_id in chunks:
                chunks[chunk_id].video_id = vid_id
                session.add(chunks[chunk_id])

    await session.commit()
    logger.info("Database seeded successfully with CSV data.")


async def seed_vector_db_if_empty():
    """
    Seeds the ChromaDB vector database from a pickle file if it is empty.
    """
    try:
        # Note: Use 'chromadb' and port 8000 when running inside the Docker network
        chroma_client = Chroma(
            host="chromadb",
            port="8000",
        )
        
        # 'langchain' is the default collection name used by langchain_chroma
        result = chroma_client.get(include=["metadatas"])
        
        # Check if there's any data already
        if len(result['ids']) > 0:
            logger.info("Vector database already has data, skipping seeding.")
            return

        logger.info("Seeding vector database...")
        pkl_path = os.path.join(DATA_DIR, 'vector_data_export.pkl')
        
        if not os.path.exists(pkl_path):
            logger.warning(f"Seed file not found: {pkl_path}")
            return

        with open(pkl_path, 'rb') as f:
            loaded_data = pickle.load(f)

        chroma_client._collection.add(
            ids=loaded_data['ids'],
            embeddings=loaded_data['embeddings'],
            metadatas=loaded_data.get('metadatas', None), # In case metadatas is optional
            documents=loaded_data['documents']
        )
        logger.info("Vector database seeded successfully.")
        
    except Exception as e:
        logger.error(f"Failed to seed vector database: {e}")