from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import RedirectResponse
from src.db.main import get_session
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from src.app_logger import logger
from src.models.users_schema import UserResponse, UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.users_service import UserService
from src.dependencies.services_getter import get_user_service, get_oauth_service
from src.config import get_settings
from src.utils.token_utils import decode_token, create_access_token, create_refresh_token
from jose import JWTError
from exceptions import UserAlreadyVerifiedError, UserNotFoundError, InvalidTokenError
import httpx
from src.services.oauth_service import OAuthService
from src.services.users_service import UserService

auth_router = APIRouter()

@auth_router.post('/signup', 
                  response_model=UserResponse,
                  status_code=status.HTTP_201_CREATED)
async def signup_user(user: UserCreate,
                      bg_tasks: BackgroundTasks,
                     session: AsyncSession = Depends(get_session),
                     user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.create_user(session=session,
                                               user_create=user,
                                               bg_tasks=bg_tasks)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'Error during signup: {e}')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f'Unexpected error: {e}')
    

@auth_router.get('/verify_email', status_code=status.HTTP_200_OK)
async def verify_email(token: str, 
                       session: AsyncSession = Depends(get_session),
                       user_service: UserService = Depends(get_user_service)):
    try:
        user = await user_service.verify_user_by_email(session=session, token=token)
        if user:
            #TO-DO change to RedirectResponse
            return JSONResponse(content={"message": "Email verified successfully! You can now log in."}) 
        
    except InvalidTokenError as e:
        logger.warning(f"Invalid token used for verification: {e}")

        #TO-DO change to RedirectResponse
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except UserNotFoundError as e:
        logger.warning(f"Verification attempt for a non-existent user: {e}") # Уровень WARNING лучше
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
    except UserAlreadyVerifiedError as e:
        logger.info(f"Verification attempt for an already active user: {e}") # Уровень INFO
        #TO-DO change to RedirectResponse
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        logger.error("An unexpected error occurred during email verification.", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@auth_router.get('/signin/google')
async def signin_google(oath_service: OAuthService = Depends(get_oauth_service)):

    try:
        return await oath_service.sign_in_google_redirect()
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=f'Unknown error: {e}')



@auth_router.get('/callback/google')
async def callback_google(code: str,
                          state: str, 
                          session: AsyncSession = Depends(get_session),
                          user_service: UserService = Depends(get_user_service),
                          oath_service: OAuthService = Depends(get_oauth_service)):
     
    user_data = await oath_service.google_callback_logic(code=code,
                                                             state=state)
    
    user_from_oauth = await user_service.get_or_create_oauth_user(
            session=session,
            name=user_data['user_name'],
            email=user_data['user_email'],
            provider='google'
        )

    access_token = create_access_token(user_id=user_from_oauth.id)
    refresh_token = create_refresh_token(user_id=user_from_oauth.id)

    frontend_url = "http://localhost:3000/account"
    response = RedirectResponse(url=frontend_url)

    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=True,
        path='/',
        max_age=900
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,
        path="/api/auth/refresh"
    )

    return response
    


    
    

