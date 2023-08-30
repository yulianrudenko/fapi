from app import schemas


def test_get_posts_success(authorized_client, test_posts):
    response = authorized_client.get('posts/')
    json = response.json()
    assert response.status_code == 200
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


def test_get_posts_fail(client):
    # Not authenticated
    response = client.get('posts/')
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}
