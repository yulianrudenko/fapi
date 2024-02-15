from sqlalchemy.orm import Session

from app.selectors import get_user
from app import models


def test_get_user(user_obj: models.User, session: Session):
    # User found
    assert \
        get_user(id=user_obj.id, db=session).first_name == \
        session.query(models.User).filter(models.User.id == user_obj.id).first().first_name

    # User not found
    assert get_user(id=user_obj.id+100, db=session) is None
