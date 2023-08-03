from .db import SessionLocal
from . import models


def get_user(id: int| str, db = None) -> models.User | None:
    if not db:
        db = SessionLocal()
    user_obj = db.query(models.User).filter(models.User.id == id).first()
    return user_obj
