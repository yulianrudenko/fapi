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

    # Send same request again
    response = client.post('users/', json={
        'email': 'test@mail.com', 'first_name': 'Joe', 'password': '12345', 'birth_date': '2000-01-01'
    })
    assert response.status_code == 409
    assert response.json() == {'detail': 'User with this email already exists'}


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


def test_get_user_success(authorized_client: TestClient, user_obj: models.User):
    response = authorized_client.get(url=f'users/{user_obj.id}')
    assert response.status_code == 200
    user_data = schemas.UserOut(**response.json())
    assert 'id' in user_data.dict()


def test_get_user_fail(authorized_client: TestClient, user_obj: models.User):
    # No authentication
    response = authorized_client.get(f'users/{user_obj.id}', headers={'Authorization': ''})
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}

    # User not found
    response = authorized_client.get(url=f'users/{user_obj.id+9999}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

