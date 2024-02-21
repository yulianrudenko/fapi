import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import users, posts


app = FastAPI()

app.include_router(users.router, tags=['users'])
app.include_router(posts.router, tags=['posts'])
app.mount('/static', StaticFiles(directory=settings.STATIC_DIR), name='static')
app.mount('/media', StaticFiles(directory=settings.MEDIA_DIR), name='media')

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex='^(http://)?127.0.0.1:[0-9]+(/.*)?$',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
