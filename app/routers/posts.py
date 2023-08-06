from fastapi import (
    APIRouter,
    Depends, 
    HTTPException,
    Path, Query, Body,
    status,
)
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.auth import get_current_user
from app import models, schemas

router = APIRouter(prefix='/posts', tags=['posts'])


@router.get('/', status_code=status.HTTP_200_OK)
async def get_posts(
    ids: list[int] | None = Query(default=None, title='Posts IDs', description='List of Posts IDs to retrieve'),
    limit: int | None = Query(default=100, gte=1, le=10000, title='Limit', description='Limit the qty of posts items'),
    offset: int | None = Query(default=0, gte=0, title='Offset', description='Post index to start retrieving from'),
    title: str | None = Query(default=None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[schemas.PostOut]:
    posts_query = db.query(models.Post, func.count(models.PostLike.post_id).label('likes_count')) \
        .join(models.PostLike, models.PostLike.post_id == models.Post.id, isouter=True).group_by(models.Post.id)
    if ids:
        posts_query = posts_query.filter(models.User.id.in_(ids))
    if title:
        posts_query = posts_query.filter(models.Post.title.contains(title))
    posts = posts_query.offset(offset).limit(limit).all()
    posts = [schemas.PostOut(**post.__dict__, likes_count=likes_count) for post, likes_count in posts]
    return posts


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: schemas.PostCreate = Body(),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.PostOut:
    post_data = {**post_data.dict(), 'user': current_user}
    post_obj = models.Post(**post_data)
    db.add(post_obj)
    db.commit()
    db.refresh(post_obj)
    return post_obj


@router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_post(
    id: int = Path(title='Post ID', description='ID of the post to retrieve'),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.PostOut:
    post_obj = db.query(models.Post, func.count(models.PostLike.post_id).label('likes_count')) \
        .join(models.PostLike, models.PostLike.post_id == models.Post.id, isouter=True).group_by(models.Post.id) \
        .filter(models.Post.id == id).first()
    if post_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    post_obj = schemas.PostOut(**post_obj[0].__dict__, likes_count=post_obj[1]) 
    return post_obj


@router.patch('/{id}', status_code=status.HTTP_200_OK)
async def update_post(
    id: int = Path(title='Post ID', description='ID of the post to update'),
    post_data: schemas.PostUpdate = Body(),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.PostOut:
    post_query = db.query(models.Post).filter(models.Post.id == id, models.Post.user_id == current_user.id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    post_query.update(post_data.dict(exclude_unset=True))
    db.commit()
    return post_query.first()


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int = Path(title='Post ID', description='ID of the post to delete'),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    post_deleted = db.query(models.Post). \
        filter(models.Post.id == id, models.Post.user_id == current_user.id).delete()
    print(post_deleted)
    if not post_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    db.commit()


@router.post('/{post_id}/like', status_code=status.HTTP_200_OK)
async def like_post(
    post_id: int = Path(title='Post ID', description='ID of the post to like'),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.MessageSuccess:
    # Check if provided post exists
    post_obj = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')

    # Check if like for this post and this user already exists 
    like_obj: bool = db.query(models.PostLike).filter(
        models.PostLike.post_id == post_id,
        models.PostLike.user_id == current_user.id
    ).first()
    if like_obj:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='like already exists')

    # Create PostLike object
    like_obj = models.PostLike(post=post_obj, user=current_user)
    db.add(like_obj)
    db.commit()
    db.refresh(like_obj)
    return {'message': 'success'}


@router.post('/{post_id}/unlike', status_code=status.HTTP_200_OK)
async def unlike_post(
    post_id: int = Path(title='Post ID', description='ID of the post to unlike'),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.MessageSuccess:
    like_query = db.query(models.PostLike).filter(models.Post.id == post_id, models.User.id == current_user.id)
    if not like_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='like not found')
    like_query.delete()
    db.commit()
    return {'message': 'success'}
