"""
Main FastAPI application for Job Planner Assistant.
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from config import settings
from database import init_database
from api import router
from admin_api import admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Job Planner Assistant API...")
    
    # Create data directories
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/logs", exist_ok=True)
    os.makedirs("./data/chromadb", exist_ok=True)
    
    # Initialize database
    init_database()
    logger.info("Database initialized")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Job Planner Assistant API...")


# Create FastAPI application
app = FastAPI(
    title="Job Planner Assistant API",
    version="1.0.0",
    description="A multi-agent system for intelligent job search planning",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(router, prefix="/api")
app.include_router(admin_router, prefix="/api")

# 创建admin文件夹并挂载静态文件
os.makedirs("./admin", exist_ok=True)
app.mount("/admin", StaticFiles(directory="admin", html=True), name="admin")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Job Planner Assistant API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/api/health",
        "admin_url": "/admin",
        "frontend_admin_url": "http://localhost:3000/admin"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        "./data/logs/app.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="30 days"
    )
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

