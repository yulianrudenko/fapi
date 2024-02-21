import os
import uuid

from unittest.mock import patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app import schemas
from app import models
from app.auth import get_current_user
from app.config import settings

from .conftest import TestClient


class TestRegister:
    def test_success(self, client: TestClient):
        response = client.post('users/', json={
            'email': 'test@mail.com', 'first_name': 'Joe', 'password': '12345', 'birth_date': '2000-01-01'
        })
        assert response.status_code == 201
        new_user = schemas.UserOut(**response.json())
        assert 'id' in new_user.dict()

    def test_fail(self, client: TestClient, user_obj: models.User):
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


class TestLogin:
    def test_login_success(self, client: TestClient, session: Session, user_obj: models.User):
        response = client.post('users/login/', data={'username': user_obj.email, 'password': user_obj.plain_password})
        assert response.status_code == 200
        data = schemas.Token(**response.json())
        assert data.type == 'bearer'
        assert get_current_user(token=data.access_token, db=session) == user_obj  # Validate token

    def test_login_fail(self, client: TestClient, session: Session, user_obj: models.User):
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


class TestGetUser:
    def test_success(self, authorized_client: TestClient, user_obj: models.User):
        response = authorized_client.get(url=f'users/{user_obj.id}')
        assert response.status_code == 200
        user_data = schemas.UserOut(**response.json())
        assert user_data.id == user_obj.id

    def test_fail(self, authorized_client: TestClient, user_obj: models.User):
        # Not authenticated
        response = authorized_client.get(f'users/{user_obj.id}', headers={'Authorization': ''})
        assert response.status_code == 401
        assert response.json() == {'detail': 'Not authenticated'}

        # User not found
        response = authorized_client.get(url=f'users/{user_obj.id+100}')
        assert response.status_code == 404
        assert response.json() == {'detail': 'User not found'}


class TestUpdateUser:
    def test_success(self, authorized_client: TestClient, user_obj: models.User):
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

    def test_fail(self, authorized_client: TestClient):
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


class TestUploadPicture:
    def test_success_with_no_image_previously_set_and_with_image_set(
        self,
        authorized_client: TestClient,
        session: Session,
        user_obj: models.User
    ):
        assert user_obj.profile_picture == None
        # Image folder empty
        user_images_dir = os.path.join(settings.MEDIA_DIR, settings.USER_IMAGES_FOLDER)
        user_images = os.listdir(user_images_dir)
        assert user_images == []

        # Upload image
        with open(os.path.join(settings.STATIC_DIR, 'image.jpg'), 'rb') as image_file:
            response = authorized_client.post('users/picture', files={
                'file': ('image.jpg', image_file, 'image/jpeg')
            })
        assert response.status_code == 200
        assert response.json() == {'status': True}

        # Image saved to appropriate directory
        user_images = os.listdir(user_images_dir)
        assert len(user_images) == 1

        # Check if extension in jpg and file name is valid UUID object
        image_uuid_str, image_extension = user_images[0].split('.')
        assert image_extension == 'jpg'
        uuid_obj = uuid.UUID(image_uuid_str, version=4)
        assert str(uuid_obj) == image_uuid_str

        # User DB data updated
        session.refresh(user_obj)
        assert user_obj.profile_picture == f'{image_uuid_str}.{image_extension}'

        # Upload another image 
        with open(os.path.join(settings.STATIC_DIR, 'image.jpg'), 'rb') as image_file:
            response = authorized_client.post('users/picture', files={
                'file': ('image.jpg', image_file, 'image/jpeg')
            })
        assert response.status_code == 200
        assert response.json() == {'status': True}

        # Image saved to appropriate directory
        user_images = os.listdir(user_images_dir)
        assert len(user_images) == 1

        # Check if extension in jpg and file name is valid UUID object and is different from previous picture
        new_image_uuid_str, image_extension = user_images[0].split('.')
        assert new_image_uuid_str != image_uuid_str 
        assert image_extension == 'jpg'
        uuid_obj = uuid.UUID(new_image_uuid_str, version=4)
        assert str(uuid_obj) == new_image_uuid_str

        # User DB data updated
        session.refresh(user_obj)
        assert user_obj.profile_picture == f'{new_image_uuid_str}.{image_extension}'

    def test_error_uploading_image(
        self,
        authorized_client: TestClient,
        session: Session,
        user_obj: models.User
    ):
        user_obj.profile_picture = 'test'
        session.commit()

        with \
            open(os.path.join(settings.STATIC_DIR, 'image.jpg'), 'rb') as image_file, \
            patch('app.routers.users.local_storage.upload_user_image', return_value=None):
            response = authorized_client.post('users/picture', files={
                'file': ('image.jpg', image_file, 'image/jpeg')
            })
        assert response.status_code == 400
        assert response.json() == {'detail': 'Error uploading picture.'}

        session.refresh(user_obj)
        assert user_obj.profile_picture == 'test'  # DB data hasn't changed


class TestDeletePicture:
    def test_success_user_has_no_picture_set(self, authorized_client: TestClient, session: Session, user_obj: models.User):
        assert user_obj.profile_picture == None
        response = authorized_client.delete('users/picture')
        assert response.status_code == 204
        session.refresh(user_obj)
        assert user_obj.profile_picture == None

    def test_success_user_has_picture_set(self, authorized_client: TestClient, session: Session, user_obj: models.User):
        # Mock user image
        user_images_dir = os.path.join(settings.MEDIA_DIR, settings.USER_IMAGES_FOLDER)
        with open(os.path.join(settings.STATIC_DIR, 'image.jpg'), 'rb') as image_bin, \
            open(os.path.join(user_images_dir, 'image.jpg'), 'wb') as image_file:
            image_file.write(image_bin.read())
        assert os.listdir(user_images_dir) == ['image.jpg']
        user_obj.profile_picture = 'image.jpg'
        session.commit()

        response = authorized_client.delete('users/picture')
        assert response.status_code == 204
        assert os.listdir(user_images_dir) == []  # Deleted
        session.refresh(user_obj)
        assert user_obj.profile_picture == None  # DB updated
