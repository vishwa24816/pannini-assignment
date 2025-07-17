import os
import pytest
from app.app import create_app, db
from app.models.user import User

@pytest.fixture(scope='module')
def test_client():
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()

def test_signup(test_client):
    response = test_client.post('/signup', json={
        'username': 'testteacher',
        'password': 'password',
        'role': 'teacher'
    })
    assert response.status_code == 201
    assert b'User created successfully' in response.data

    response = test_client.post('/signup', json={
        'username': 'teststudent',
        'password': 'password',
        'role': 'student'
    })
    assert response.status_code == 201
    assert b'User created successfully' in response.data

def test_login(test_client):
    response = test_client.post('/login', json={
        'username': 'testteacher',
        'password': 'password'
    })
    assert response.status_code == 200
    assert b'token' in response.data

def test_create_assignment(test_client):
    login_response = test_client.post('/login', json={
        'username': 'testteacher',
        'password': 'password'
    })
    token = login_response.get_json()['token']

    response = test_client.post('/assignments', json={
        'title': 'Test Assignment',
        'description': 'Test Description'
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    assert b'Assignment created successfully' in response.data
