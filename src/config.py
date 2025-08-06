from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from dotenv import find_dotenv

class MailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    model_config = SettingsConfigDict(env_prefix='MAIL_', 
                                      env_file=find_dotenv(),
                                      extra='ignore')

class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(env_prefix='REDIS_', env_file=find_dotenv(),
                                      extra='ignore')

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_prefix='DATABASE_', 
                                      env_file=find_dotenv(),
                                      extra='ignore')    

class JwtSettings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGO: str

    model_config = SettingsConfigDict(env_prefix='JWT_',
                                      env_file=find_dotenv(),
                                      extra='ignore')   

class GoogleAuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_CALLBACK_REDIRECT_URI: str
    GOOGLE_TOKEN_URI: str
    GOOGLE_AUTH_URI: str
    GOOGLE_USER_INFO_URI: str

    model_config = SettingsConfigDict(env_prefix='GOOGLE_', 
                                      env_file=find_dotenv(),
                                      extra='ignore')   


class Settings(BaseSettings):
    mail: MailSettings
    redis: RedisSettings
    database: DatabaseSettings
    jwt: JwtSettings
    google: GoogleAuthSettings


#change later to global object
@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore