from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.logging import LoggingMiddleware
from app.middleware.authorization import JWTAuthMiddleware
from app.utils.simple_logging import setup_logging
from app.routes.test import router as test_router
from app.routes.auth import router as auth_router

# Setup structured logging
setup_logging()

app = FastAPI(
    title="SprintSync API",
    description="A modern project management and sprint tracking application",
    version="1.0.0"
)

# Add middlewares in order (last added = first executed)
# 1. Logging middleware (outermost - logs everything)
app.add_middleware(LoggingMiddleware)

# 2. JWT Authentication middleware
app.add_middleware(JWTAuthMiddleware)

# 3. CORS middleware (should be after auth to allow preflight requests)
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

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(test_router, prefix="/api/v1", tags=["test"])