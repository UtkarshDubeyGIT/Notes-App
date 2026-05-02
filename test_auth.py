import pytest
from flask import session
from website import create_app, db
from website.models import User, Note
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test_secret_key',
        'WTF_CSRF_ENABLED': False
    })

    with app.app_context():
        db.create_all()
        
        user1 = User(
            email='user1@example.com',
            password=generate_password_hash('password123', method='pbkdf2:sha1'),
            first_name='User1'
        )
        user2 = User(
            email='user2@example.com',
            password=generate_password_hash('password123', method='pbkdf2:sha1'),
            first_name='User2'
        )
        
        db.session.add_all([user1, user2])
        db.session.commit()
        
        note1 = Note(data='User1 Note 1', user_id=user1.id)
        note2 = Note(data='User1 Note 2', user_id=user1.id)
        note3 = Note(data='User2 Note 1', user_id=user2.id)
        
        db.session.add_all([note1, note2, note3])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login_user(client, email, password):
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)


def test_home_requires_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')


def test_delete_note_requires_login(client):
    response = client.post('/delete-note', json={'noteId': 1})
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')


def test_user_can_see_own_notes(client, app):
    with app.app_context():
        login_user(client, 'user1@example.com', 'password123')
        
        response = client.get('/')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        assert 'User1 Note 1' in response_text
        assert 'User1 Note 2' in response_text
        assert 'User2 Note 1' not in response_text


def test_user_cannot_see_other_users_notes(client, app):
    with app.app_context():
        login_user(client, 'user2@example.com', 'password123')
        
        response = client.get('/')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        assert 'User2 Note 1' in response_text
        assert 'User1 Note 1' not in response_text
        assert 'User1 Note 2' not in response_text


def test_user_can_delete_own_note(client, app):
    with app.app_context():
        login_user(client, 'user1@example.com', 'password123')
        
        note = Note.query.filter_by(data='User1 Note 1').first()
        assert note is not None
        
        response = client.post('/delete-note', json={'noteId': note.id})
        assert response.status_code == 200
        
        deleted_note = Note.query.filter_by(data='User1 Note 1').first()
        assert deleted_note is None


def test_user_cannot_delete_other_users_note(client, app):
    with app.app_context():
        login_user(client, 'user1@example.com', 'password123')
        
        user2_note = Note.query.filter_by(data='User2 Note 1').first()
        assert user2_note is not None
        
        response = client.post('/delete-note', json={'noteId': user2_note.id})
        assert response.status_code == 200
        
        still_exists = Note.query.filter_by(data='User2 Note 1').first()
        assert still_exists is not None


def test_user_cannot_access_note_by_id_directly(client, app):
    with app.app_context():
        login_user(client, 'user1@example.com', 'password123')
        
        user2_note = Note.query.filter_by(data='User2 Note 1').first()
        assert user2_note is not None
        
        response = client.get(f'/delete-note', follow_redirects=True)
        assert 'User2 Note 1' not in response.data.decode('utf-8')
