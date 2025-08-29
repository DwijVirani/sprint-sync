from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
import logging
import time

from app.utils.simple_logging import log_exception

router = APIRouter()
logger = logging.getLogger("sprintsync.routes.test")


@router.get("/test/success")
async def test_success():
    """Test endpoint that succeeds."""
    logger.info("Test success endpoint called", extra={"endpoint": "test_success"})
    return {"message": "Success!", "timestamp": time.time()}


@router.get("/test/error")
async def test_error():
    """Test endpoint that raises an error."""
    logger.info("Test error endpoint called", extra={"endpoint": "test_error"})
    
    # This will trigger our error logging
    raise HTTPException(status_code=400, detail="This is a test error")


@router.get("/test/exception")
async def test_exception():
    """Test endpoint that raises an unhandled exception."""
    logger.info("Test exception endpoint called", extra={"endpoint": "test_exception"})
    
    # This will trigger our exception logging middleware
    raise ValueError("This is a test unhandled exception")


@router.post("/test/data")
async def test_post_data(data: Dict[str, Any]):
    """Test POST endpoint with data."""
    logger.info("Test POST endpoint called", extra={
        "endpoint": "test_post_data",
        "data_keys": list(data.keys())
    })
    
    return {
        "message": "Data received successfully",
        "received_keys": list(data.keys()),
        "timestamp": time.time()
    }


@router.get("/test/slow")
async def test_slow_endpoint():
    """Test endpoint that takes time (for latency testing)."""
    logger.info("Slow endpoint called", extra={"endpoint": "test_slow"})
    
    # Simulate some processing time
    import asyncio
    await asyncio.sleep(2)
    
    return {"message": "Slow operation completed", "timestamp": time.time()}
