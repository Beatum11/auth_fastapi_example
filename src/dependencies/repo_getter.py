from fastapi import Depends
from src.repos.user_repo import SqlAlchemyUserRepository
from src.db.main import get_session
from sqlalchemy.ext.asyncio import AsyncSession

def get_user_repository(session: AsyncSession = Depends(get_session)) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)