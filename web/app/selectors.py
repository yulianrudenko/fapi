from sqlalchemy.orm import Session

from . import models


def get_user(id: int| str, db: Session | None = None) -> models.User | None:
    user_obj = db.query(models.User).filter(models.User.id == id).first()
    return user_obj
