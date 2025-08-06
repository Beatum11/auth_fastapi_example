from httpx import Response as httpx_response
from fastapi.responses import RedirectResponse
import secrets
import hashlib
import base64
from src.exceptions import InvalidCodeVerifierError, GoogleAPIError
import httpx
from src.app_logger import logger
from src.config import Settings
from src.db.redis import RedisClient

class OAuthService():
    
    def __init__(self, settings: Settings, redis_client: RedisClient) -> None:
        self.settings = settings
        self.redis_client = redis_client
    
    async def sign_in_google_redirect(self):
        
        pkce_params = await self._prepare_pkce_state()

        google_client_id = self.settings.google.GOOGLE_CLIENT_ID
        redirect_uri = self.settings.google.GOOGLE_CALLBACK_REDIRECT_URI
        google_auth_uri = self.settings.google.GOOGLE_AUTH_URI

        return RedirectResponse(url=
            f"{google_auth_uri}"
            f"response_type=code&"
            f"client_id={google_client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=openid%20email%20profile&"
            f"access_type=offline&"
            f"state={pkce_params['state']}"
            f"code_challenge={pkce_params['code_challenge']}&"
            f"code_challenge_method=S256"
        )
    

    async def google_callback_logic(self, code: str, state: str) -> dict:
        """
        Returns user data from Google
        """
        token_data = await self._google_token_getter(code=code, state=state)
        return await self._user_data_getter(token_data)

        
    
    async def _user_data_getter(self, token_data: dict) -> dict:
        """
        Fetches user profile information from Google's userinfo endpoint
        """

        g_access_token = token_data.get('access_token')

        userinfo_url = self.settings.google.GOOGLE_USER_INFO_URI
        headers = {"Authorization": f"Bearer {g_access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)

        data = self._check_response_success(response)

        user_email = data.get('email')
        user_name = data.get('name')
        user_sub = data.get('sub')
        user_email_verified = data.get('email_verified')

        return {'user_name': user_name, 'user_email': user_email, 'sub': user_sub,
                'email_verified': user_email_verified}



    async def _google_token_getter(self, code: str, state: str) -> dict:
        """
        Exchanges an authorization code for Google API tokens using PKCE
        """
        
        code_verifier = await self.redis_client.get_and_delete_pkce_verifier(state=state)
        if not code_verifier:
            raise InvalidCodeVerifierError('Invalid state, sorry google')

        token_url =  self.settings.google.GOOGLE_TOKEN_URI
        GOOGLE_CLIENT_ID = self.settings.google.GOOGLE_CLIENT_ID
        GOOGLE_CLIENT_SECRET = self.settings.google.GOOGLE_CLIENT_SECRET
        REDIRECT_URI = self.settings.google.GOOGLE_CALLBACK_REDIRECT_URI

        data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            "grant_type": "authorization_code",
            "code_verifier": code_verifier
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)

        return self._check_response_success(response=response)


    def _check_response_success(self, response: httpx_response) -> dict:
            
            """
                Checks response status and returns json if it's 200, otherwise raises an error.
            """
            
            if response.status_code == 200:
                return response.json()

            try:
                error_data = response.json()
                e_message = f'Error from Google API: {error_data.get("error_description", error_data)}'
            except Exception:
                e_message = f'Google API returned status {response.status_code} with non-JSON body'
                
            logger.error(e_message)
            raise GoogleAPIError(e_message)
                    

    async def _prepare_pkce_state(self) -> dict:

        """
            Creates code_verifier, state and code_challenge 
            in order to complete OAuth2 flow
        """

        code_verifier = secrets.token_urlsafe(32)
        state = secrets.token_hex(16)

        await self.redis_client.save_pkce_verifier(code_verifier=code_verifier, state=state)

        digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
        code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode('ascii')

        return {'state': state, 'code_challenge': code_challenge}

    
        