"""
Simplified FastAPI application for the web scraper - only /scrape endpoint.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from app.api.routes import router
from app.core.config import settings
from app.utils.logger import logger
from app import __version__


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Create FastAPI app
    app = FastAPI(
        title="Web Scraper API",
        description="Simplified web scraper using crawl4AI for comprehensive data extraction",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests and their processing time."""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

    # Add exception handler for HTTPException
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "error_type": "HTTPException",
                "timestamp": logger._get_timestamp() if hasattr(logger, '_get_timestamp') 
                             else time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception handler caught: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_type": "InternalError",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "details": {"message": str(exc)}
            }
        )
    
    # Include API routes
    app.include_router(router, prefix="/api/v1")
    
    # Add startup event
    @app.on_event("startup")
    async def startup_event():
        """Application startup event."""
        logger.info(f"Starting Web Scraper API v{__version__}")
        logger.info(f"API will be available at: http://{settings.api_host}:{settings.api_port}")
        logger.info(f"Documentation available at: http://{settings.api_host}:{settings.api_port}/docs")
        logger.info("Only /api/v1/scrape endpoint is available")
    
    # Add shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown event."""
        logger.info("Shutting down Web Scraper API")
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,  # Enable auto-reload for development
        log_level=settings.log_level.lower()
    ) 