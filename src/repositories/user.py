from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.schemas.user import UserCreate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_in: UserCreate, hashed_password: str) -> User:
        user = User(email=user_in.email, name=user_in.name, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()
    
    async def get_by_id(self, user_id: int) -> User:
        result = await self.session.get(User, user_id)
        return result
    
    async def list(self, limit: int = 10, offset: int = 0) -> list[User]:
        result = await self.session.execute(
            select(User).offset(offset).limit(limit)
        )
        return result.scalars().all()