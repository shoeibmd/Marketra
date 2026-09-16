from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)


@app.get("/healthz", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "version": settings.VERSION}


@app.get(f"{settings.API_V1_STR}/ping", tags=["System"])
async def ping() -> dict[str, str]:
    return {"message": "pong"}
