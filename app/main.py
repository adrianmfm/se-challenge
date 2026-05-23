from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1 import users
from app.core.logging import logger

app = FastAPI(
    title="User Management API",
    description="RESTful API for user management with full CRUD operations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(users.router, prefix="/api/v1")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
