from fastapi import FastAPI

from src.router.router import router

app = FastAPI()
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Hello hitoq!"}
