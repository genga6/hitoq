import os

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware

from src.logging_config import configure_logging, get_logger
from src.middleware import LoggingMiddleware
from src.router import auth, router

# Configure logging before creating the app
configure_logging()
logger = get_logger(__name__)

# Initialize Sentry for error monitoring
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FastApiIntegration(auto_enable=True),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,  # Adjust based on traffic
        environment=os.getenv("ENVIRONMENT", "development"),
    )
    logger.info("Sentry initialized", dsn_provided=True)
else:
    logger.warning("Sentry DSN not provided, error monitoring disabled")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="hitoQ API",
    description="This is the API for the hitoQ application.",
    version="0.1.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Frontend URLs from environment variable
frontend_urls = os.getenv("FRONTEND_URLS", "http://localhost:5173").split(",")
origins = [url.strip() for url in frontend_urls]

# CORS configuration for production
allow_methods = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,PATCH").split(",")
allow_headers = os.getenv(
    "CORS_ALLOW_HEADERS", "Content-Type,Authorization,Accept"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[method.strip() for method in allow_methods],
    allow_headers=[header.strip() for header in allow_headers],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

# Add logging middleware
app.add_middleware(LoggingMiddleware)

app.include_router(router.username_router)
app.include_router(router.global_router)
app.include_router(router.resource_router)
app.include_router(auth.auth_router, prefix="/auth", tags=["Authentication"])


@app.get("/")
@limiter.limit("30/minute")
def root(request: Request):
    logger.info("Root endpoint accessed", client_ip=get_remote_address(request))
    return {"message": "Welcome to hitoQ API!"}


@app.get("/health")
def health():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "service": "hitoq-api", "version": "0.1.0"}
