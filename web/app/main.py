from fastapi import FastAPI

from .routers import users, posts


app = FastAPI()
app.include_router(users.router, tags=['users'])
app.include_router(posts.router, tags=['posts'])
