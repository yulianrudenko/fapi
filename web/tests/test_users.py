from datetime import datetime, timedelta

from app import schemas
from app import models
from app.auth import get_current_user

from .conftest import TestClient


def test_register_success(client: TestClient):
    response = client.post('users/', json={
        'email': 'test@mail.com', 'first_name': 'Joe', 'password': '12345', 'birth_date': '2000-01-01'
    })
    assert response.status_code == 201
    new_user = schemas.UserOut(**response.json())
    assert 'id' in new_user.dict()


def test_register_fail(client: TestClient, user_obj):
    # Email taken
    # Send same request again
    response = client.post('users/', json={
        'email': user_obj.email, 'first_name': 'Joe', 'password': '12345', 'birth_date': '2000-01-01'
    })
    assert response.status_code == 409
    assert response.json() == {'detail': 'User with this email already exists'}

    # Invalid birth date
    response = client.post('users/', json={
        'email': 'test@mail.com', 'first_name': 'Joe', 'password': '12345',
        'birth_date': (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
    })
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'birth_date'], 'msg': 'You must be over 18 to use this service', 'type': 'value_error'}]}


def test_login_success(client: TestClient, session, user_obj: models.User):
    response = client.post('users/login/', data={'username': user_obj.email, 'password': user_obj.plain_password})
    assert response.status_code == 200
    data = schemas.Token(**response.json())
    assert data.type == 'bearer'
    assert get_current_user(token=data.access_token, db=session) == session.query(models.User).first()  # Validate token


def test_login_fail(client: TestClient, session, user_obj: models.User):
    # Invalid payload
    response = client.post('users/login/', data={'username': None, 'password': user_obj.plain_password})
    assert response.status_code == 422
    response = client.post('users/login/', data={'username': user_obj.email, 'password': None})
    assert response.status_code == 422

    # Invalid password
    response = client.post('users/login/', data={'username': user_obj.email, 'password': f'{user_obj.plain_password}!@#$%'})
    assert response.status_code == 403
    assert response.json() == {'detail': 'Invalid credentials'}

    # Unexisting user email
    session.query(models.User).filter(models.User.id == user_obj.id).delete()
    response = client.post('users/login/', data={'username': user_obj.email, 'password': user_obj.plain_password})
    assert response.status_code == 403
    assert response.json() == {'detail': 'Invalid credentials'}


def test_update_user_success(authorized_client: TestClient, user_obj: models.User):
    response = authorized_client.patch(url='users/', json={})
    assert response.status_code == 200
    user_data = schemas.UserOut(**response.json())
    assert user_data.id == user_obj.id

    response = authorized_client.patch(url='users/', json={'first_name': 'new name', 'birth_date': '2000-12-12', 'id': 0})
    assert response.status_code == 200
    user_data = schemas.UserOut(**response.json())
    assert user_data.id != 0
    assert user_data.id == user_obj.id
    assert user_data.first_name == 'new name'
    assert user_data.birth_date.strftime('%Y-%m-%d') == '2000-12-12'


def test_update_user_fail(authorized_client: TestClient):
    # Not authenticated
    response = authorized_client.patch(url='users/', headers={'Authorization': ''}, json={})
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}

    # Invalid birth date
    response = authorized_client.patch('users/', json={
        'birth_date': (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
    })
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'birth_date'], 'msg': 'You must be over 18 to use this service', 'type': 'value_error'}]}


def test_get_user_success(authorized_client: TestClient, user_obj: models.User):
    response = authorized_client.get(url=f'users/{user_obj.id}')
    assert response.status_code == 200
    user_data = schemas.UserOut(**response.json())
    assert user_data.id == user_obj.id


def test_get_user_fail(authorized_client: TestClient, user_obj: models.User):
    # Not authenticated
    response = authorized_client.get(f'users/{user_obj.id}', headers={'Authorization': ''})
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}

    # User not found
    response = authorized_client.get(url=f'users/{user_obj.id+9999}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

