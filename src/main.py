from fastapi import FastAPI

from router import user

app = FastAPI()
app.include_router(user.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Hello hitoq!"}
