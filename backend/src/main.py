import os

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware

from src.config.limiter import limiter
from src.config.logging_config import configure_logging, get_logger
from src.middleware.csrf import CSRFMiddleware
from src.middleware.logging import LoggingMiddleware
from src.router import auth
from src.router.block_router import block_router
from src.router.message_router import message_router
from src.router.notification_router import notification_router
from src.router.profile_router import profile_router
from src.router.qna_router import answers_router, qna_router, questions_router
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


app = FastAPI(
    title="hitoQ API",
    description="Q&A-based profile viewer API with messaging functionality",
    version="0.1.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization operations",
        },
        {"name": "Users", "description": "User management operations"},
        {"name": "Profile", "description": "User profile and Q&A management"},
        {"name": "Messages", "description": "User messaging system"},
        {"name": "Notifications", "description": "User notification management"},
        {"name": "Questions", "description": "Question template management"},
        {"name": "Answers", "description": "Answer management and retrieval"},
        {"name": "Visits", "description": "User visit tracking"},
        {"name": "Username", "description": "Username availability and validation"},
        {"name": "Blocks", "description": "User blocking and reporting functionality"},
    ],
    contact={"name": "Gengaru", "email": "gengaru617science@gmail.com"},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

frontend_urls = os.getenv("FRONTEND_URLS", "http://localhost:5173").split(",")
origins = [url.strip() for url in frontend_urls]

allow_methods = os.getenv(
    "CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS"
).split(",")
allow_headers_raw = os.getenv(
    "CORS_ALLOW_HEADERS", "Content-Type,Authorization,Accept,X-CSRFToken"
)
allow_headers = allow_headers_raw.split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[method.strip() for method in allow_methods],
    allow_headers=[header.strip() for header in allow_headers],
    expose_headers=["X-CSRFToken"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

if os.getenv("ENVIRONMENT") != "test":
    app.add_middleware(CSRFMiddleware)

app.add_middleware(LoggingMiddleware)

app.include_router(username_router, tags=["Username"])
app.include_router(user_router, tags=["Users"])
app.include_router(profile_router, tags=["Profile"])
app.include_router(message_router, tags=["Messages"])
app.include_router(notification_router, tags=["Notifications"])
app.include_router(qna_router, tags=["Profile"])
app.include_router(questions_router, tags=["Questions"])
app.include_router(answers_router, tags=["Answers"])
app.include_router(visit_router, tags=["Visits"])
app.include_router(block_router, tags=["Blocks"])
app.include_router(auth.auth_router, prefix="/auth", tags=["Authentication"])


@app.get(
    "/",
    summary="Root endpoint",
    description="Returns welcome message for the hitoQ API",
    response_description="Welcome message",
)
@limiter.limit("30/minute")
def root(request: Request):
    logger.info("Root endpoint accessed", client_ip=get_remote_address(request))
    return {"message": "Welcome to hitoQ API!"}


@app.get(
    "/health",
    summary="Health check",
    description="Returns the health status of the API service",
    response_description="Service health status",
)
def health():
    return {"status": "healthy", "service": "hitoq-api", "version": "0.1.0"}
