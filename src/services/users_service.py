from fastapi import Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.users_schema import UserLogin, UserCreate
from src.dependencies.repo_getter import get_user_repository
from sqlalchemy.ext.asyncio import AsyncSession
from src.repos.interfaces.i_user_repo import IUserRepository
from src.models.users import User
from src.utils.password_utils import hash_password
from src.utils.token_utils import *
from src.app_logger import logger
from src.utils.email_utils import send_verification_email
from jose import JWTError
from src.exceptions import InvalidTokenError, UserAlreadyVerifiedError, UserNotFoundError
import uuid

class UserService():
    def __init__(self,user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    async def create_user(self, session: AsyncSession, 
                          user_create: UserCreate,
                          bg_tasks: BackgroundTasks) -> dict:
        
        existing_user = await self.user_repo.get_user_by_email(user_create.email)
        if existing_user:
            #need to change on custom error
            logger.error('attempt to create user that already exists')
            raise ValueError('User already exists')
        
        user_to_db = User(**user_create.model_dump(exclude={'password'}))


        password_hash = hash_password(user_create.password)
        user_to_db.password_hash = password_hash

    # need to use uow later
        try:
            created_user: User = await self.user_repo.create_user(user_to_db)
            await session.commit()
            await session.refresh(created_user)

            ver_token = create_verification_token(created_user.id)
            bg_tasks.add_task(send_verification_email, created_user.email, ver_token)

            return {'user': created_user, 'message': 'Registration successful. Please check your email to verify your account.'}
        
        except Exception as e:
            logger.error(f'Error during user creation: {e}')
            await session.rollback()
            #need to change on custom error
            raise
        

    async def verify_user_by_email(self, session: AsyncSession, token: str) -> User:
        try:
            payload = decode_token(token)
            user_id_str = payload.get('sub')
            token_type = payload.get('type')

            if token_type != 'verification':
                raise InvalidTokenError("Invalid token type")
            
            if not user_id_str:
                raise InvalidTokenError("There is no user Id")
            
        except JWTError:
            raise InvalidTokenError("Invalid or expired token")
        

        user_uuid = uuid.UUID(user_id_str)
        existing_user = await self.user_repo.get_user_by_id(user_uuid)

        if existing_user is None:
            raise UserNotFoundError('User not Found')
        
        if existing_user.is_active:
            raise UserAlreadyVerifiedError('email has been already verified')
        
        activated_user = await self.user_repo.activate_user(existing_user)
        await session.commit()
        await session.refresh(activated_user)
        return activated_user
    

    async def get_or_create_oauth_user(self, session: AsyncSession, 
                                       name: str, 
                                       email: str,
                                       provider: str) -> User:
        
        user = await self.user_repo.get_user_by_email(email)
        if user:
            return user
        
        data = {
            'email': email,
            'name': name,
            'is_active': True,
            'password_hash': None,
            'auth_provider': provider
        }

        new_user = User(**data)

        created_user = await self.user_repo.create_user(user=new_user)
        await session.commit()
        return created_user



        

