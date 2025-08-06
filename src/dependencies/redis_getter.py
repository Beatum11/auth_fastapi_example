from fastapi import Depends
from src.config import Settings, get_settings
from src.db.redis import RedisClient

redis_client: RedisClient = RedisClient(get_settings())

def redis_getter():
    return redis_client
