from typing import Optional
from sqlalchemy import select
# from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.repos.interfaces.i_user_repo import IUserRepository
from src.models.users import User
import uuid

class SqlAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def get_user_by_id(self, id: uuid.UUID) -> Optional[User]:
        statement = select(User).where(User.id == id)
        res = await self.session.execute(statement)
        return res.scalars().first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        res = await self.session.execute(statement)
        return res.scalars().first()

   #need to test this 
    async def activate_user(self, user: User) -> User:
        """Activate user after email verification"""

        user.is_active = True
        await self.session.flush()
        await self.session.refresh(user)
        return user

        
        
