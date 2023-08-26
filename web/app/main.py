from fastapi import FastAPI

from .routers import users, posts
from .db import engine
from . import models


app = FastAPI()

app.include_router(users.router)
app.include_router(posts.router)
