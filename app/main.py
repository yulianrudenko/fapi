from fastapi import FastAPI

from .db import engine
from . import models
from .routers import users, posts


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(users.router)
app.include_router(posts.router)
