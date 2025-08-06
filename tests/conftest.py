import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from src.db.main import Base, get_session
import uuid
from src import app


DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL)

TestAsyncSession = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

@pytest_asyncio.fixture(scope="session")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="module")
async def test_client(db_session):

    with patch('src.db.main.init_db', new_callable=AsyncMock), \
         patch('src.db.main.close_db', new_callable=AsyncMock), \
         patch('src.db.main.AsyncSession', TestAsyncSession):
        
        async def override_get_session():
            async with TestAsyncSession() as session:
                try:
                    yield session
                except Exception:
                    await session.rollback()
                    raise
                finally:
                    await session.close()
        
        app.dependency_overrides[get_session] = override_get_session
        
        transport = ASGITransport(app=app)
        
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            yield client
        
        app.dependency_overrides.clear()