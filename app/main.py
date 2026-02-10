from fastapi import FastAPI

from app.routers.app_router import app_router

app = FastAPI(title="Log Handler")

app.include_router(app_router)
