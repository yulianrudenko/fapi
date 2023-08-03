from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app import selectors
from app.db import get_db
from app.utils import hash_password, verify_password
from app.auth import create_access_token, get_current_user

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.UserOut:
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='user with this email already exists')
    user.password = hash_password(user.password)
    user_obj = models.User(**user.dict())
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


@router.post('/login/', status_code=status.HTTP_200_OK)
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> schemas.Token:
    user_obj = db.query(models.User).filter(models.User.email == credentials.username).first()
    if user_obj and verify_password(plain=credentials.password, hashed=user_obj.password):
        return {
            'access_token': create_access_token({'user_id': user_obj.id}),
            'type': 'bearer'
        }
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='invalid credentials')


@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_user(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> schemas.UserOut:
    user_obj = selectors.get_user(id=id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    return user_obj
