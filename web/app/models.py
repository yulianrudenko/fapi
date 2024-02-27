import uuid

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    UUID,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import  relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP, DATE

from app.db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    birth_date = Column(DATE, nullable=False)
    profile_picture = Column(String(120), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    posts: Mapped[set["Post"]] = relationship(back_populates="user")
    likes: Mapped[set["PostLike"]] = relationship(back_populates="user")
    chats_sent: Mapped[set["Chat"]] = relationship(back_populates="user1", foreign_keys="Chat.user1_id")
    chats_received: Mapped[set["Chat"]] = relationship(back_populates="user2", foreign_keys="Chat.user2_id")
    chat_messages: Mapped[set["ChatMessage"]] = relationship(back_populates="user")


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    is_active = Column(Boolean, server_default="TRUE", nullable=False)
    published_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.current_timestamp(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="posts")
    likes: Mapped["PostLike"] = relationship(back_populates="post")


class PostLike(Base):
    __tablename__ = "post_like"

    post_id: Mapped[int] = mapped_column(ForeignKey("post.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    post: Mapped["Post"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship(back_populates="likes")


class Chat(Base):
    __tablename__ = "chat"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    user1_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    user2_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    user1: Mapped["User"] = relationship(back_populates="chats_sent", foreign_keys=[user1_id])
    user2: Mapped["User"] = relationship(back_populates="chats_received", foreign_keys=[user2_id])
    messages: Mapped["ChatMessage"] = relationship(back_populates="chat")

    __table_args__ = (
        CheckConstraint('user1_id != user2_id', name='check_user1_not_equal_user'),
        UniqueConstraint('user1_id', 'user2_id', name='unq_user1_user2'),
    )


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.uuid4] = mapped_column(ForeignKey("chat.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    user: Mapped["User"] = relationship(back_populates="chat_messages")
