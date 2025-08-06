from fastapi import Depends
from src.dependencies.repo_getter import get_user_repository

from src.repos.interfaces.i_user_repo import IUserRepository
from src.services.oauth_service import OAuthService
from src.config import get_settings, Settings
from src.dependencies.redis_getter import redis_getter
from src.db.redis import RedisClient
from services.users_service import UserService


def get_user_service(user_repo: IUserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo=user_repo)

def get_oauth_service(settings: Settings = Depends(get_settings),
                      redis_client: RedisClient = Depends(redis_getter)) -> OAuthService:
    
    return OAuthService(settings=settings, redis_client=redis_client)
