from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import  relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP, DATE
from sqlalchemy.sql import func

from .db import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    birth_date = Column(DATE, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    posts = relationship('Post', back_populates='user')
    likes = relationship('PostLike', back_populates='user')


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    is_active = Column(Boolean, server_default='TRUE', nullable=False)
    published_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.current_timestamp(), nullable=False)

    user = relationship(User, back_populates='posts')
    likes = relationship('PostLike', back_populates='post')


class PostLike(Base):
    __tablename__ = 'post_like'

    post_id = Column(Integer, ForeignKey('post.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)

    user = relationship(User, back_populates='likes')
    post = relationship(Post, back_populates='likes')
