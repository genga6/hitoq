from fastapi import FastAPI

from src.router import qna, user, utils

app = FastAPI(
    title="hitoQ API",
    description="This is the API for the hitoQ application.",
    version="0.1.0",
)

app.include_router(user.router)
app.include_router(qna.router)
app.include_router(utils.router)


@app.get("/")
def root():
    return {"message": "Welcome to hitoQ API!"}
