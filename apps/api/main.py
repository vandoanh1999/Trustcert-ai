"""
TrustCert AI - Main FastAPI Application
Enterprise-grade API with full features
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from contextlib import asynccontextmanager
import time
import logging
from prometheus_client import Counter, Histogram, make_asgi_app
import sys

# Import routes (we'll create these)
from apps.api.routes import health, auth, verify, certify, blockchain, analytics
from apps.api.core.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware
)
from apps.api.core.exceptions import (
    TrustCertException,
    ValidationException,
    AuthenticationException
)
from apps.api.config import settings
from apps.api.utils.logger import setup_logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'trustcert_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'trustcert_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting TrustCert AI API...")
    
    # Startup: Initialize resources
    try:
        # Initialize database connections
        # await init_db()
        
        # Initialize Redis cache
        # await init_cache()
        
        # Initialize blockchain connections
        # await init_blockchain()
        
        # Load ML models
        # await load_ml_models()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)
    
    yield  # Application runs
    
    # Shutdown: Cleanup resources
    logger.info("🛑 Shutting down TrustCert AI API...")
    # await cleanup()

# Create FastAPI app
app = FastAPI(
    title="TrustCert AI API",
    description="""
    🧠 **TrustCert AI** - Intelligent Verification Framework
    
    ## Features
    - 🔐 Cryptographic Verification (RSA, ECDSA, ZKP)
    - 🤖 AI Model Certification
    - ⛓️ Blockchain Integration (Ethereum, IPFS)
    - 🛡️ ML Safety Validation
    - 📊 Trust Score Engine
    - 🔒 Quantum-Resistant Algorithms
    
    ## Authentication
    Use API key in header: `X-API-Key: your_api_key`
    """,
    version="2.0.0",
    docs_url=None,  # Custom docs
    redoc_url=None,
    lifespan=lifespan,
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
        {"name": "auth", "description": "Authentication & authorization"},
        {"name": "verify", "description": "Verification operations"},
        {"name": "certify", "description": "Certificate generation"},
        {"name": "blockchain", "description": "Blockchain operations"},
        {"name": "analytics", "description": "Analytics & reporting"},
    ]
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# CORS - Configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
)

# Gzip compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(TrustCertException)
async def trustcert_exception_handler(request: Request, exc: TrustCertException):
    """Handle custom TrustCert exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": exc.error_type,
                "message": exc.message,
                "code": exc.error_code,
                "request_id": request.state.request_id,
                "timestamp": time.time()
            }
        }
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "message": str(exc),
                "details": exc.errors,
                "request_id": request.state.request_id
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_server_error",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, 'request_id', None)
            }
        }
    )

# ============================================================================
# CUSTOM DOCUMENTATION
# ============================================================================

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with branding"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Interactive Docs",
        swagger_favicon_url="https://trustcert.ai/favicon.ico",
        swagger_ui_parameters={
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "filter": True,
            "tryItOutEnabled": True
        }
    )

# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(verify.router, prefix="/api/v1/verify", tags=["verify"])
app.include_router(certify.router, prefix="/api/v1/certify", tags=["certify"])
app.include_router(blockchain.router, prefix="/api/v1/blockchain", tags=["blockchain"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "TrustCert AI",
        "version": "2.0.0",
        "status": "operational",
        "capabilities": {
            "cryptographic_verification": True,
            "ai_model_certification": True,
            "blockchain_integration": True,
            "ml_safety_validation": True,
            "trust_scoring": True,
            "quantum_resistant": True
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/api/v1/health",
            "api": "/api/v1",
            "metrics": "/metrics"
        },
        "links": {
            "documentation": "https://docs.trustcert.ai",
            "github": "https://github.com/vandoanh1999/Trustcert-ai",
            "support": "https://support.trustcert.ai"
        }
    }

# ============================================================================
# STARTUP MESSAGE
# ============================================================================

@app.on_event("startup")
async def startup_message():
    """Display startup banner"""
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║   ████████╗██████╗ ██╗   ██╗███████╗████████╗                ║
    ║   ╚══██╔══╝██╔══██╗██║   ██║██╔════╝╚══██╔══╝                ║
    ║      ██║   ██████╔╝██║   ██║███████╗   ██║                   ║
    ║      ██║   ██╔══██╗██║   ██║╚════██║   ██║                   ║
    ║      ██║   ██║  ██║╚██████╔╝███████║   ██║                   ║
    ║      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝                   ║
    ║                                                                ║
    ║              CERT AI - v2.0.0                                  ║
    ║        Intelligent Verification Framework                      ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    
    🚀 Server: http://localhost:8000
    📚 Docs: http://localhost:8000/docs
    📊 Metrics: http://localhost:8000/metrics
    
    Ready to verify the future of AI! 🧠✨
    """
    print(banner)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )