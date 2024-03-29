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

from ..db import get_db
from ..auth import get_current_user
from .. import models, schemas

router = APIRouter(prefix='/posts', tags=['posts'])


@router.get('/', status_code=status.HTTP_200_OK)
async def get_posts(
    id: list[int] | None = Query(default=None, title='Posts IDs', description='List of Posts IDs to retrieve'),
    limit: int | None = Query(default=100, gte=1, le=10000, title='Limit', description='Limit the qty of posts items'),
    offset: int | None = Query(default=0, gte=0, title='Offset', description='Post index to start retrieving from'),
    title: str | None = Query(default=None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[schemas.PostOut]:
    posts_query = db.query(models.Post, func.count(models.PostLike.post_id).label('likes_count')) \
        .join(models.PostLike, models.PostLike.post_id == models.Post.id, isouter=True) \
        .group_by(models.Post.id) \
        .order_by(models.Post.published_at.desc())
    if id:
        posts_query = posts_query.filter(models.Post.id.in_(id))
    if title:
        posts_query = posts_query.filter(models.Post.title.contains(title))
    posts = posts_query.offset(offset).limit(limit).all()
    posts = [{**post.__dict__, 'likes_count': likes_count} for post, likes_count in posts]
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
    post_obj.likes_count = 0
    return post_obj


@router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_post(
    id: int = Path(title='Post ID', description='ID of the post to retrieve'),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.PostOut:
    post_obj = db.query(models.Post).filter(models.Post.id == id).first()
    if post_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    post_obj.likes_count = db.query(models.PostLike).filter(models.PostLike.post_id == id).count()
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    post_query.update(post_data.dict(exclude_unset=True))
    db.commit()
    post_obj = post_query.first()
    post_obj.likes_count = db.query(models.PostLike).filter(models.PostLike.post_id == id).count()
    return post_obj


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int = Path(title='Post ID', description='ID of the post to delete'),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    post_deleted = db.query(models.Post). \
        filter(models.Post.id == id, models.Post.user_id == current_user.id).delete()
    if not post_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    db.commit()
    return None


@router.post('/{post_id}/like', status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: int = Path(title='Post ID', description='ID of the post to like'),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    # Check if provided post exists
    post_obj = db.query(models.Post).filter(models.Post.id == post_id, models.Post.is_active == True).first()
    if not post_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

    # Check if like for this post and this user already exists 
    like_obj: bool = db.query(models.PostLike).filter(
        models.PostLike.post_id == post_id,
        models.PostLike.user_id == current_user.id
    ).first()
    if like_obj:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Like already exists')

    # Create PostLike object
    like_obj = models.PostLike(post=post_obj, user=current_user)
    db.add(like_obj)
    db.commit()
    db.refresh(like_obj)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post('/{post_id}/unlike', status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(
    post_id: int = Path(title='Post ID', description='ID of the post to unlike'),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    like_query = db.query(models.PostLike).filter(models.PostLike.post_id == post_id, models.PostLike.user == current_user)
    if not like_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Like not found')
    like_query.delete()
    db.commit()
    return None
