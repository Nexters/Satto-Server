from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config.config import app_config
from src.config.lifespan import lifespan
from src.config.middleware import DBMiddleware
from src.four_pillars.router import four_pillar_router
from src.users.router import user_router

app = FastAPI(lifespan=lifespan, root_path="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.CORS_ORIGIN.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(DBMiddleware)

app.include_router(user_router)
app.include_router(four_pillar_router)
