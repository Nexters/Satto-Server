from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config.config import app_config
from src.config.lifespan import lifespan
from src.config.middleware import DBMiddleware
from src.users.router import user_router
from src.lotto.router import lotto_router
from src.fortune.admin_router import admin_fortune_router
from src.fortune.user_router import user_fortune_router

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
app.include_router(lotto_router)
app.include_router(admin_fortune_router)
app.include_router(user_fortune_router)