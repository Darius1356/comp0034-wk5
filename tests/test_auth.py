import string
import secrets
import pytest
from faker import Faker
from sqlalchemy import exists
from paralympics.models import User
from paralympics import db


# Additional fixtures for authentication.
# I have not put these in conftest.py to keep them separate from the solution to last week's activity.
@pytest.fixture(scope='session')
def new_user(app):
    """Create a new user and add to the database.

    Adds a new User to the database and also returns the JSON for a new user.

    The scope is session as we need the user to be there throughout for testing the logged in functions.

    """
    user_json = {'email': 'tester@mytesting.com', 'password': 'PlainTextPassword'}

    with app.app_context():
        user = User(email=user_json['email'])
        user.set_password(user_json['password'])
        db.session.add(user)
        db.session.commit()

    yield user_json

    # Remove the region from the database at the end of the test if it still exists
    with app.app_context():
        user_exists = db.session.query(exists().where(User.email == user_json['email'])).scalar()
        if user_exists:
            db.session.delete(user)
            db.session.commit()


@pytest.fixture(scope='function')
def random_user_json():
    """Generates a random email and password for testing and returns as JSON."""
    dummy = Faker()
    dummy_email = dummy.email()
    # Generate an eight-character alphanumeric password
    alphabet = string.ascii_letters + string.digits
    dummy_password = ''.join(secrets.choice(alphabet) for i in range(8))
    return {'email': dummy_email, 'password': dummy_password}


@pytest.fixture(scope="function")
def login(client, new_user, app):
    """Returns login response"""
    # Login
    # If login fails then the fixture fails. It may be possible to 'mock' this instead if you want to investigate it.
    response = client.post('/login', json=new_user, content_type="application/json")
    # Get returned json data from the login function
    data = response.json
    yield data


# Authentication tests
def test_register_success(client, random_user_json):
    """
    GIVEN a valid format email and password for a user not already registered
    WHEN an account is created
    THEN the status code should be 201
    """
    user_register = client.post('/register', json=random_user_json, content_type="application/json")
    assert user_register.status_code == 201


def test_login_success(client, new_user):
    """
    GIVEN a valid format email and password for a user already registered
    WHEN /login is called
    THEN the status code should be 201
    """
    user_register = client.post('/login', json=new_user, content_type="application/json")
    assert user_register.status_code == 201


def test_user_not_logged_in_cannot_edit_region(client, new_user, new_region):
    """
    GIVEN a registered user that is not logged in
    AND a route that is protected by login
    AND a new Region that can be edited
    WHEN a PATCH request to /regions/<code> is made
    THEN the HTTP response status code should be 401 with message 'Authentication token missing
    """
    new_region_notes = {'notes': 'An updated note'}
    code = new_region['NOC']
    response = client.patch(f"/regions/{code}", json=new_region_notes)
    assert response.status_code == 401


def test_user_logged_in_user_can_edit_region(app, client, new_user, login, new_region):
    """
    GIVEN a registered user that is successfully logged in
    AND a route that is protected by login
    AND a new Region that can be edited
    WHEN a PATCH request to /regions/<code> is made
    THEN the HTTP status code should be 200
    AND the response content should include the message 'Region <NOC_code> updated'
    """
    # pass the token in the headers of the HTTP request
    token = login['token']
    headers = {
        'content-type': "application/json",
        'Authorization': token
    }
    new_region_notes = {'notes': 'An updated note'}
    code = new_region['NOC']
    response = client.patch(f"/regions/{code}", json=new_region_notes, headers=headers)
    assert response.json == {"message": "Region NEW updated."}
    assert response.status_code == 200
