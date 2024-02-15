from app.selectors import get_user
from app import models


def test_get_user(client, user_obj: models.User, session):
    assert \
        get_user(id=user_obj.id, db=session).first_name == \
        session.query(models.User).filter(models.User.id == user_obj.id).first().first_name
