from fastapi import FastAPI

from test.mock_router import router

app = FastAPI()
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Mock server running"}
