import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions.handlers import register_exception_handlers
from app.api.v1.routers import router as v1_router
from app.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    await init_db()
    yield

app = FastAPI(
    title="reelvee - Backend API",
    description="""This is the backend API for reelvee platform. Here you can find the API endpoints and their documentation for reelvee.""",
    version="1.0.0",
    contact={
        "name": "reelvee Support",
        "email": "support@reelvee.com",
        "url": "https://reelvee.com",
    },
    lifespan=lifespan,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
        },
    },
)

app.include_router(v1_router)

register_exception_handlers(app)

# Configure CORS
origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "https://wasel-black.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)