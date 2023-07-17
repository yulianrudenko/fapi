from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas
from ..utils import hash_password

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.UserOut:
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='user with this email already exists')
    user.password = hash_password(user.password)
    user_obj = models.User(**user.dict())
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user


@router.get('/{id}/', status_code=status.HTTP_200_OK)
def get_user(id: int, db: Session = Depends(get_db)) -> schemas.UserOut:
    user_obj = db.query(models.User).filter(models.User.id == id).first()
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    return user_obj
