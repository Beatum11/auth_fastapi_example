from redis.asyncio import Redis
from src.config import get_settings, Settings

class RedisClient():
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        self.redis_client = Redis(
            host=self.settings.redis.REDIS_HOST,
            port=self.settings.redis.REDIS_PORT,
            db=0,
            decode_responses=True
        )


    async def add_to_blocklist(self, jti: str, expires_at: int=3600) -> None:
        """
        Add a token's unique ID (jti) to the Redis.

        Parameters:
            jti (str): Unique identifier of the token.
            expires_at (int): Time-to-live (TTL) in seconds
        """
        await self.redis_client.set(
            name=f"blocklist:{jti}",
            value="",
            ex=expires_at
        )

    async def is_token_blocked(self, jti: str) -> bool:
        return await self.redis_client.get(f"blocklist:{jti}") is not None


    async def save_pkce_verifier(self, code_verifier: str, state: str) -> None:
        await self.redis_client.set(
            name=f"pkce:{state}",
            value=code_verifier,
            ex=600
        )

    async def get_and_delete_pkce_verifier(self, state: str) -> str | None:
        
        key = f"pkce:{state}"
        pipe = self.redis_client.pipeline()
        pipe.get(key)
        pipe.delete(key)

        res = await pipe.execute()

        code_verifier = res[0]
        if code_verifier is not None:
            return code_verifier
        return None
    


