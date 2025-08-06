from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.db.main import init_db, close_db
from src.app_logger import logger
from src.views.auth_routes import auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        yield
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    finally:
        logger.info("Closing connections")
        await close_db()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],  
    allow_headers=["*"],      
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(auth_router, prefix=f'/api/auth')