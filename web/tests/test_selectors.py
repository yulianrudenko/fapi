from app.selectors import get_user
from app import models


def test_get_user(user_obj, session):
    assert \
        get_user(id=user_obj.id).id == \
        session.query(models.User).filter(models.User.id == user_obj.id).first().id
