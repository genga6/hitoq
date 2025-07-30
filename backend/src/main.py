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

from src.config.logging_config import configure_logging, get_logger
from src.middleware.logging import LoggingMiddleware
from src.router import auth
from src.router.bucket_list_router import bucket_list_router
from src.router.profile_router import profile_router
from src.router.qna_router import qna_router, questions_router
from src.router.user_router import user_router
from src.router.username_router import username_router
from src.router.visit_router import visit_router

configure_logging()
logger = get_logger(__name__)

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "development"),
    )
    logger.info("Sentry initialized", dsn_provided=True)
else:
    logger.warning("Sentry DSN not provided, error monitoring disabled")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="hitoQ API",
    description="This is the API for the hitoQ application.",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

frontend_urls = os.getenv("FRONTEND_URLS", "http://localhost:5173").split(",")
origins = [url.strip() for url in frontend_urls]

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
app.add_middleware(LoggingMiddleware)

app.include_router(username_router)
app.include_router(user_router)
app.include_router(profile_router)
app.include_router(bucket_list_router)
app.include_router(qna_router)
app.include_router(questions_router)
app.include_router(visit_router)
app.include_router(auth.auth_router, prefix="/auth", tags=["Authentication"])


@app.get("/")
@limiter.limit("30/minute")
def root(request: Request):
    logger.info("Root endpoint accessed", client_ip=get_remote_address(request))
    return {"message": "Welcome to hitoQ API!"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "hitoq-api", "version": "0.1.0"}
