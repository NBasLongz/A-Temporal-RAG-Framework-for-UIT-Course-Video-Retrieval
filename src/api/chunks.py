from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.chunk import ChunkResponse

from src.dependencies import get_chunk_service
from typing import List

router = APIRouter(prefix="/chunks", tags=["Chunks"])

@router.get("/", response_model=List[ChunkResponse])
async def list_chunks(
    chunk_service = Depends(get_chunk_service),
    limit: int = 10,
    offset: int = 0
):
    # Placeholder implementation
    return await chunk_service.list_chunks(limit, offset)

@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: str, 
    chunk_service = Depends(get_chunk_service)

):
    # Placeholder implementation
    chunk = await chunk_service.get_chunk_by_id(chunk_id)

    if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Chunk not found"
            )
    return chunk

@router.get("/video/{video_id}", response_model=List[ChunkResponse])
async def get_chunks_by_video_id(
    video_id: str,
    from_timestamp: int = 0,
    to_timestamp: int = 0,
    chunk_service = Depends(get_chunk_service)
):
    # Placeholder implementation
    chunks = await chunk_service.get_chunk_by_video_id(video_id, from_timestamp, to_timestamp)

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No chunks found for the given video ID and timestamp range"
        )
    return chunks