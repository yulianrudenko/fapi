from fastapi import (
    APIRouter,
    Response,
    HTTPException,
    Path, Query, Body,
    status,
    Depends,
)
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.auth import get_current_user
from app import models, schemas

router = APIRouter(prefix='/chats', tags=['chats'])


@router.get('/start/{opposite_user_id}', status_code=status.HTTP_201_CREATED)
def start_chat(opposite_user_id: str, current_user: models.User = Depends(get_current_user)):
    pass
