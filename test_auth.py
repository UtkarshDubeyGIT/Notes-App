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
        assert response.status_code == 403
        
        response_json = response.get_json()
        assert 'error' in response_json
        assert 'Unauthorized' in response_json['error']
        
        still_exists = Note.query.filter_by(data='User2 Note 1').first()
        assert still_exists is not None


def test_user_cannot_delete_note_by_id_directly_via_get(client, app):
    with app.app_context():
        login_user(client, 'user1@example.com', 'password123')
        
        response = client.get('/delete-note', follow_redirects=True)
        assert response.status_code == 405


def test_user_cannot_delete_nonexistent_note(client, app):
    with app.app_context():
        login_user(client, 'user1@example.com', 'password123')
        
        response = client.post('/delete-note', json={'noteId': 999999})
        assert response.status_code == 404
        
        response_json = response.get_json()
        assert 'error' in response_json
        assert 'Note not found' in response_json['error']


def test_new_note_belongs_to_current_user(client, app):
    with app.app_context():
        login_user(client, 'user1@example.com', 'password123')
        
        user1 = User.query.filter_by(email='user1@example.com').first()
        initial_notes_count = Note.query.filter_by(user_id=user1.id).count()
        
        response = client.post('/', data={
            'note': 'New Test Note'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        new_note = Note.query.filter_by(data='New Test Note').first()
        assert new_note is not None
        assert new_note.user_id == user1.id
        
        updated_count = Note.query.filter_by(user_id=user1.id).count()
        assert updated_count == initial_notes_count + 1
        
        response_text = response.data.decode('utf-8')
        assert 'New Test Note' in response_text


def test_other_user_cannot_see_new_note(client, app):
    with app.app_context():
        login_user(client, 'user1@example.com', 'password123')
        
        client.post('/', data={
            'note': 'User1 Private Note'
        }, follow_redirects=True)
        
        private_note = Note.query.filter_by(data='User1 Private Note').first()
        assert private_note is not None
        
        client.get('/logout', follow_redirects=True)
        
        login_user(client, 'user2@example.com', 'password123')
        
        response = client.get('/')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        assert 'User1 Private Note' not in response_text
