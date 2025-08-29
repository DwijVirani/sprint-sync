from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.logging import LoggingMiddleware
from app.utils.simple_logging import setup_logging
from app.routes.test import router as test_router

# Setup structured logging
setup_logging()

app = FastAPI(
    title="SprintSync API",
    description="A modern project management and sprint tracking application",
    version="1.0.0"
)

# Add logging middleware first (it should be the outermost middleware)
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to SprintSync API"}

@app.get("/health-check")
async def health_check():
    return {"status": "Healthy"}

# Include test routes
app.include_router(test_router, prefix="/api/v1", tags=["test"])