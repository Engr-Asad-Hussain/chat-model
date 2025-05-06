from fastapi import FastAPI

from app.routers.v1 import router


def start_app():
    app = FastAPI()
    app.include_router(router)
    return app


app = start_app()


@app.get("/app")
async def root():
    return {"message": "Application is up and running ..."}
