from app import schemas
from app import models

from .conftest import TestClient


def test_get_posts_success(authorized_client: TestClient, test_posts: list[models.Post]):
    response = authorized_client.get('posts/')
    assert response.status_code == 200
    json = response.json()
    assert len(json) == len(test_posts)
    assert len(list(map(lambda post: schemas.PostOut(**post), json))) == len(test_posts)

    # With "ids" query parameter
    response = authorized_client.get(f'posts/?id={test_posts[0].id}&id={test_posts[1].id}')
    json = response.json()
    assert response.status_code == 200
    assert len(json) == 2
    assert len(list(map(lambda post: schemas.PostOut(**post), json))) == 2
    assert all([str(post['id']) in [str(test_posts[0].id), str(test_posts[1].id)] for post in json])

    # With "title" query parameter
    response = authorized_client.get(f'posts/?title=Title')
    json = response.json()
    assert response.status_code == 200
    assert len(json) == len(test_posts)
    assert len(list(map(lambda post: schemas.PostOut(**post), json))) == len(test_posts)
    assert all([str(post['id']) in [str(p.id) for p in test_posts] for post in json])

    response = authorized_client.get(f'posts/?title=Title1')
    json = response.json()
    assert response.status_code == 200
    assert len(json) == 1
    assert json[0]['title'] == 'Title1'
    assert json[0]['content'] == 'Content1'

    # With "limit" query parameter
    response = authorized_client.get(f'posts/?limit=1')
    json = response.json()
    assert response.status_code == 200
    assert len(json) == 1
    assert 'id' in json[0]
    assert lambda post: schemas.PostOut(**json[0])

    # With "offset" query parameter
    response = authorized_client.get(f'posts/?offset=1')
    json = response.json()
    assert response.status_code == 200
    assert len(json) == 4
    assert all([str(post['id']) in [str(p.id) for p in test_posts] for post in json])

    # Parameters combined
    posts_ids = [str(post.id) for post in test_posts]
    response = authorized_client.get(f'posts/?id={posts_ids[0]}&id={posts_ids[1]}&id={posts_ids[2]}&limit=2&offset=1&title=Title')
    json = response.json()
    assert response.status_code == 200
    assert len(json) == 2
    assert all([str(post['id']) in posts_ids[:3] for post in json])


def test_get_posts_fail(client: TestClient):
    # Not authenticated
    response = client.get('posts/')
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


def test_create_post_success(authorized_client: TestClient, user_obj: models.User):
    user_id = user_obj.id
    response = authorized_client.post('posts/', json={'title': 'new title', 'content': 'new content'})
    assert response.status_code == 201
    json = response.json()
    assert schemas.PostOut(**json)
    assert type(json['id']) is int
    assert json['user_id'] == user_id
    assert json['likes_count'] == 0


def test_create_post_fail(authorized_client: TestClient):
    # Invalid payload
    response = authorized_client.post('posts/', json={'content': 'new content'})
    assert response.status_code == 422

    # Not authenticated
    authorized_client.headers = {}
    response = authorized_client.get('posts/')
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


def test_get_post_success(authorized_client: TestClient, test_posts: list[models.Post]):
    test_post = test_posts[0]
    response = authorized_client.get(f'posts/{test_post.id}')
    assert response.status_code == 200
    json = response.json()
    assert json['id'] == test_post.id
    assert json['title'] == test_post.title
    assert json['content'] == test_post.content
    assert json['likes_count'] == 0


def test_get_post_fail(authorized_client: TestClient, test_posts: list[models.Post]):
    # Not found
    response = authorized_client.get('posts/0')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Post not found'}

    # Not authenticated
    authorized_client.headers = {}
    response = authorized_client.get(f'posts/{test_posts[0].id}')
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_post_success(authorized_client: TestClient, test_posts: list[models.Post]):
    test_post = test_posts[0]
    response = authorized_client.patch(f'posts/{test_post.id}', json={'title': 'updated title', 'content': 'updated content'})
    assert response.status_code == 200
    json = response.json()
    assert json['id'] == test_post.id
    assert json['title'] == 'updated title'
    assert json['content'] == 'updated content'
    assert test_post.title == 'updated title'
    assert test_post.content == 'updated content'

    response = authorized_client.patch(f'posts/{test_post.id}', json={'id': 0})
    assert response.status_code == 200
    json = response.json()
    assert json['id'] == test_post.id


def test_update_post_fail(authorized_client: TestClient, session, test_posts: list[models.Post], extra_user_obj: models.User):
    test_post = test_posts[0]
    # Invalid payload
    response = authorized_client.patch(f'posts/{test_post.id}', json={'title': 'a'})
    assert response.status_code == 422
    response = authorized_client.patch(f'posts/{test_post.id}')
    assert response.status_code == 422

    # Not found
    response = authorized_client.patch('posts/0', json={})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Post not found'}

    # Not authenticated
    authorized_headers = authorized_client.headers
    authorized_client.headers = {}
    response = authorized_client.patch(f'posts/{test_post.id}')
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}
    authorized_client.headers = authorized_headers

    # Trying to update post that was not created by user
    session.query(models.Post).filter(models.Post.id == test_post.id).update({'user_id': extra_user_obj.id})
    response = authorized_client.patch(f'posts/{test_post.id}', json={'title': 'updated title', 'content': 'updated content'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Post not found'}


def test_delete_post_success(authorized_client: TestClient, test_posts: list[models.Post], session):
    test_post = test_posts[0]
    assert session.query(models.Post).filter(models.Post.id == test_post.id).count() == 1
    assert session.query(models.Post).count() == len(test_posts)

    response = authorized_client.delete(f'posts/{test_post.id}')
    assert response.status_code == 204
    assert session.query(models.Post).filter(models.Post.id == test_post.id).count() == 0
    assert session.query(models.Post).count() == len(test_posts) - 1


def test_delete_post_fail(authorized_client: TestClient, session, test_posts: list[models.Post], extra_user_obj: models.User):
    test_post_id = test_posts[0].id
    # Not found
    response = authorized_client.delete('posts/0')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Post not found'}

    # Not authenticated
    authorized_headers = authorized_client.headers
    authorized_client.headers = {}
    response = authorized_client.patch(f'posts/{test_post_id}')
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}
    authorized_client.headers = authorized_headers

    # Trying to delete post that was not created by user
    session.query(models.Post).filter(models.Post.id == test_post_id).update({'user_id': extra_user_obj.id})
    response = authorized_client.delete(f'posts/{test_post_id}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Post not found'}