import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

from app import models
from app.main import app
from app.db import get_db, Base
from app.config import settings
from app.utils import hash_password
from app.auth import create_access_token


engine = create_engine(settings.TESTS_DB_URL)
TestSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
fake = Faker()

@pytest.fixture(scope='function')
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope='function')
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app=app)


@pytest.fixture(scope='function')
def user_obj(session):
    plain_password = fake.password()
    user_obj = models.User(email=fake.email(), first_name=fake.first_name(), password=hash_password(plain_password), birth_date='2000-01-01')
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    user_obj.plain_password = plain_password
    return user_obj


@pytest.fixture(scope='function')
def extra_user_obj(session):
    plain_password = fake.password()
    user_obj = models.User(email=fake.email(), first_name=fake.first_name(), password=hash_password(plain_password), birth_date='2000-01-01')
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    user_obj.plain_password = plain_password
    return user_obj


@pytest.fixture(scope='function')
def authorized_client(client, user_obj):
    client.headers = {'Authorization': f'Bearer {create_access_token(user_id=str(user_obj.id))}'}
    return client


@pytest.fixture(scope='function')
def test_posts(session, user_obj):
    posts_data = [{'user_id': str(user_obj.id), 'title': f'Title{n}', 'content': f'Content{n}', 'is_active': True} for n in range(1, 6)]
    posts = list(map(lambda post_data: models.Post(**post_data), posts_data))
    session.add_all(posts)
    session.commit()
    return session.query(models.Post).all()