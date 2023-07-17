from fastapi import (
    FastAPI, Depends, HTTPException,
    Path, Query, Body, Cookie, Header,
    status,
)
from sqlalchemy.orm import Session
from typing import Any

from .db import engine, get_db
from . import schemas
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post('/auth/profile')
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.UserOut:
    user.password = '1234'
    user = models.User(**user.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get('/posts')
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


@app.post('/posts')
async def create_post(
    post_data: schemas.PostCreate = Body(examples={
        'normal': {
            'summary': 'Valid',
            'description': '**Valid** payload',
            'value': {
                **schemas.PostCreate.Config.schema_extra['example']
            }
        },
        'converted': {
            'summary': 'Converted',
            'description': '**Converted** payload',
            'value': {
                **schemas.PostCreate.Config.schema_extra['example'],
                'content': 123456789,
            },
        },
        'invalid': {
            'summary': 'Invalid',
            'description': '`Invalid` payload',
            'value': {
                **schemas.PostCreate.Config.schema_extra['example'],
                'content': 12345,
            },
        },
    }),
    db: Session = Depends(get_db)
)  -> schemas.PostOut:
    post_obj = models.Post(**{**post_data.dict(), 'user': db.query(models.User).first()})
    db.add(post_obj)
    db.commit()
    db.refresh(post_obj)
    return post_obj


@app.get('/posts/{id}')
async def get_post(
    id: int = Path(title='Post ID', description='ID of the post to retrieve'),
    db: Session = Depends(get_db),
) -> schemas.PostOut:
    post_obj = db.query(models.Post).filter_by(id=id).first()
    if post_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    return post_obj


@app.patch('/posts/{id}')
async def update_post(
    id: int = Path(title='Post ID', description='ID of the post to update'),
    post_data: schemas.PostUpdate = Body(examples={
        'normal': {
            'summary': 'Valid',
            'description': '**Valid** payload',
            'value': {
                **schemas.PostUpdate.Config.schema_extra['example']
            }
        }
    }),
    db: Session = Depends(get_db)
)  -> schemas.PostOut:
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    print(post_data.dict(exclude_unset=True))
    post_query.update(post_data.dict(exclude_unset=True))
    db.commit()
    return post_query.first()
