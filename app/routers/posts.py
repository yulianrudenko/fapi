from fastapi import (
    APIRouter,
    Depends, 
    HTTPException,
    Path, Query, Body,
    status,
)
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

router = APIRouter()


@router.get('/posts', status_code=status.HTTP_200_OK)
async def get_posts(
    ids: list[int] | None = Query(
        default=None,
        title='Posts IDs', description='List of Posts IDs to retrieve',
    ),
    limit: int | None = Query(
        default=100, gte=1, le=10000,
        title='Limit', description='Limit the qty of posts items',
    ),
    offset: int | None = Query(
        default=0, gte=0,
        title='Offset', description='Post index to start retrieving from',    
    ),
    db: Session = Depends(get_db)
) -> list[schemas.PostOut]:
    if ids:
        posts_query = db.query(models.Post).filter(models.User.id.in_(ids))
    else:
        posts_query = db.query(models.Post)
    return posts_query.offset(offset).limit(limit).all()


@router.post('/posts', status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: schemas.PostCreate = Body(),
    db: Session = Depends(get_db)
)  -> schemas.PostOut:
    post_obj = models.Post(**{**post_data.dict(), 'user': db.query(models.User).first()})
    db.add(post_obj)
    db.commit()
    db.refresh(post_obj)
    return post_obj


@router.get('/posts/{id}', status_code=status.HTTP_200_OK)
async def get_post(
    id: int = Path(title='Post ID', description='ID of the post to retrieve'),
    db: Session = Depends(get_db),
) -> schemas.PostOut:
    post_obj = db.query(models.Post).filter(models.Post.id == id).first()
    if post_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    return post_obj


@router.patch('/posts/{id}', status_code=status.HTTP_200_OK)
async def update_post(
    id: int = Path(title='Post ID', description='ID of the post to update'),
    post_data: schemas.PostUpdate = Body(),
    db: Session = Depends(get_db)
)  -> schemas.PostOut:
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    post_query.update(post_data.dict(exclude_unset=True))
    db.commit()
    return post_query.first()
