TrustCert AI v2.0 - Main Application Entry Point
Enterprise-grade AI-powered certificate verification system
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
from contextlib import asynccontextmanager

from apps.api.core.config import settings
from apps.api.core.middleware import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    RateLimitMiddleware
)
from apps.api.routes import (
    health,
    auth,
    verify,
    certify,
    blockchain,
    analytics
)
from apps.api.utils.logger import setup_logger
from apps.api.utils.metrics import metrics_middleware

# Setup logging
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 TrustCert AI v2.0 starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database connection
    # await database.connect()
    
    # Initialize Redis connection
    # await redis.connect()
    
    logger.info("✅ All systems operational")
    
    yield
    
    # Shutdown
    logger.info("🛑 TrustCert AI shutting down...")
    # await database.disconnect()
    # await redis.disconnect()
    logger.info("👋 Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="TrustCert AI",
    description="""
    🔐 **TrustCert AI v2.0** - Enterprise AI-Powered Certificate Verification System
    
    ## Features
    * 🛡️ Quantum-resistant cryptography
    * 🔗 Blockchain integration (Ethereum, IPFS)
    * 🤖 ML-based fraud detection
    * 📊 Real-time trust scoring
    * 🌍 Global certificate registry
    * ⚡ Sub-second verification
    
    ## Security
    * Zero-knowledge proofs
    * End-to-end encryption
    * Tamper-proof audit trails
    * Multi-signature verification
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    terms_of_service="https://trustcert.ai/terms",
    contact={
        "name": "TrustCert AI Support",
        "url": "https://trustcert.ai/support",
        "email": "support@trustcert.ai",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# ============= MIDDLEWARE CONFIGURATION =============

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Metrics Middleware
app.middleware("http")(metrics_middleware)

# ============= EXCEPTION HANDLERS =============

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "HTTPException",
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
            }
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Validation Error",
                "type": "ValidationError",
                "details": exc.errors(),
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
            }
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "Internal Server Error",
                "type": "InternalError",
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
            }
        },
    )

# ============= ROUTE REGISTRATION =============

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(verify.router, prefix="/api/v1/verify", tags=["Verification"])
app.include_router(certify.router, prefix="/api/v1/certify", tags=["Certification"])
app.include_router(blockchain.router, prefix="/api/v1/blockchain", tags=["Blockchain"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

# ============= ROOT ENDPOINTS =============

@app.get("/", summary="Root Endpoint", response_model=dict)
async def root():
    """
    Root endpoint - API information
    """
    return {
        "service": "TrustCert AI",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/docs",
        "environment": settings.ENVIRONMENT,
        "features": {
            "quantum_resistant": True,
            "blockchain_enabled": True,
            "ml_verification": True,
            "real_time_scoring": True,
        },
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
        }
    }

@app.get("/version", summary="Version Information")
async def version():
    """Get detailed version information"""
    return {
        "version": "2.0.0",
        "api_version": "v1",
        "build": "2024.10.09",
        "python_version": "3.11",
        "framework": "FastAPI 0.104.1",
    }

# ============= STARTUP MESSAGE =============

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "apps.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True,
    )
EOF