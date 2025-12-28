"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info(
        "Starting application",
        environment=settings.environment.value,
        llm_provider=settings.llm_provider.value,
    )
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="System Doc RAG",
    description="RAG system for system design documents",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": "System Doc RAG",
        "version": "0.1.0",
        "docs": "/docs" if settings.is_development else None,
    }


# Import and include routers
from src.api.routes import admin, documents, query

app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
