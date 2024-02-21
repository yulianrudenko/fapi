from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Body,
    UploadFile
)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from .. import selectors
from ..db import get_db
from ..utils import hash_password, verify_password
from ..auth import create_access_token, get_current_user
from ..storages import local_storage

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.UserOut:
    """Register user account"""
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User with this email already exists')
    user.password = hash_password(user.password)
    user_obj = models.User(**user.dict())
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


@router.post('/login/', status_code=status.HTTP_200_OK)
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> schemas.Token:
    """Login with email and password"""
    user_obj = db.query(models.User).filter(models.User.email == credentials.username).first()
    if user_obj and verify_password(plain=credentials.password, hashed=user_obj.password):
        return {
            'access_token': create_access_token(user_id=user_obj.id),
            'type': 'bearer'
        }
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')


@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_user(
    id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.UserOut:
    """Retrieve user data"""
    user_obj = selectors.get_user(id=id, db=db)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_obj


@router.patch('/', status_code=status.HTTP_200_OK)
def update_user(
    user_data: schemas.UserUpdate = Body(),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.UserOut:
    """Update user profile"""
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user_data = user_data.dict(exclude_unset=True)
    if user_data:
        user_query.update(user_data)
        db.commit()
    user_obj = user_query.first()
    return user_obj


@router.post('/picture', status_code=status.HTTP_200_OK)
async def upload_picture(
    file: UploadFile,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.Status:
    """Upload new user profile picture and delete current if set"""
    current_picture_name = current_user.profile_picture
    new_picture_name = await local_storage.upload_user_image(file=file)

    if new_picture_name is not None:
        if current_picture_name is not None:
            await local_storage.delete_user_image(file_name=current_user.profile_picture)
        current_user.profile_picture = new_picture_name
        db.commit()
        return {'status': True}

    return JSONResponse({'detail': 'Error uploading picture.'}, status_code=status.HTTP_400_BAD_REQUEST)


@router.delete('/picture', status_code=status.HTTP_204_NO_CONTENT)
async def delete_picture(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete current user profile picture"""
    if current_user.profile_picture:
        await local_storage.delete_user_image(file_name=current_user.profile_picture)
        current_user.profile_picture = None
        db.commit()
