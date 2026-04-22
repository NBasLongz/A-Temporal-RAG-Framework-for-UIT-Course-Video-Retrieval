import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.chunk import ChunkRepository
from src.models.chunk import Chunk
from typing import Optional, List

class ChunkService:
    def __init__(self, session: AsyncSession):
        self.repository = ChunkRepository(session)

    async def get_chunk_by_id(self, chunk_id: str) -> Optional[Chunk]:
        # Convert the string to a UUID object to match the parameter
        target_uuid = uuid.UUID(chunk_id)
        
        return await self.repository.get_by_id(target_uuid)
    
    async def list_chunks(self, limit: int = 10, offset: int = 0) -> List[Chunk]:
        return await self.repository.list(limit, offset)
    
    async def get_chunk_by_video_id(self,
                                    video_id: str,
                                    from_timestamp: int = 0,
                                    to_timestamp: int = 0) -> List[Chunk]:
        target_uuid = uuid.UUID(video_id)

        # Placeholder implementation - you would implement the actual logic in the repository
        return await self.repository.get_by_video_id(target_uuid, from_timestamp, to_timestamp)