from fastapi import FastAPI

from src.router import router

app = FastAPI(
    title="hitoQ API",
    description="This is the API for the hitoQ application.",
    version="0.1.0",
)

app.include_router(router.page_router)
app.include_router(router.resource_router)


@app.get("/")
def root():
    return {"message": "Welcome to hitoQ API!"}


@app.get("/health")
def health():
    return {"status": "ok"}
