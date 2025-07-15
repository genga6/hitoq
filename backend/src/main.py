import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.router import auth, router

app = FastAPI(
    title="hitoQ API",
    description="This is the API for the hitoQ application.",
    version="0.1.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

app.include_router(router.username_router)
app.include_router(router.global_router)
app.include_router(router.resource_router)
app.include_router(auth.auth_router, prefix="/auth", tags=["Authentication"])


@app.get("/")
def root():
    return {"message": "Welcome to hitoQ API!"}


@app.get("/health")
def health():
    return {"status": "ok"}
