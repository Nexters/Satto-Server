from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config.config import app_config
from src.config.lifespan import lifespan
from src.config.middleware import DBMiddleware
from src.users.router import user_router

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.CORS_ORIGIN.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(DBMiddleware)

uri_prefix = "/api/v1"
app.include_router(user_router, prefix=uri_prefix)
