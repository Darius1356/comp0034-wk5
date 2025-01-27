import os, sys, string, secrets
sys.path.insert(0, r'C:\Users\dariu\Documents\UCL\3rd Year\Application Programming\Repositories\comp0034-wk5')
from faker import Faker
from pathlib import Path
import pytest
from sqlalchemy import exists
from paralympics import create_app, db
from paralympics.models import Region, Event, User
from paralympics.schemas import RegionSchema, EventSchema


@pytest.fixture(scope='module')
def app():
    """Fixture that creates a test app.

    The app is created with test config parameters that include a temporary database. The app is created once for
    each test module.

    Returns:
        app A Flask app with a test config
    """
    # Location for the temporary testing database
    db_path = Path(__file__).parent.parent.joinpath('data', 'paralympics_testdb.sqlite')
    test_cfg = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(db_path),
    }
    app = create_app(test_config=test_cfg)

    yield app

    # clean up / reset resources
    # Delete the test database
#    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def new_region(app):
    """Create a new region and add to the database.

    Adds a new Region to the database and also returns an instance of that Region object.
    """
    new_region_json = {'NOC': 'NEW', 'notes': None, 'region': 'A new region'}

    with app.app_context():
        region_schema = RegionSchema()
        new_region = region_schema.load(new_region_json)
        db.session.add(new_region)
        db.session.commit()

    yield new_region_json

    # Remove the region from the database at the end of the test if it still exists
    with app.app_context():
        region_exists = db.session.query(exists().where(Region.NOC == 'NEW')).scalar()
        if region_exists:
            db.session.delete(new_region)
            db.session.commit()

@pytest.fixture(scope='function')
def new_event(app):
    """Create a new region and add to the database.

    Adds a new Region to the database and also returns an instance of that Region object.
    """
    new_event_json = {'NOC': 'ITA', 'countries': '23', 'country': 'Italy', 'disabilities_included': 'Spinal injury', 'duration': 7, 'end': '25/09/1960', 'events': 113, 'highlights': 'First Games with a disability held in same venues as Olympic Games', 'host': 'Rome', 'id': 33, 'participants': 209, 'participants_f': None, 'participants_m': None, 'region': 'ITA', 'sports': 8, 'start': '18/09/1960', 'type': 'summer', 'year': 1960}

    with app.app_context():
        event_schema = EventSchema()
        new_event = event_schema.load(new_event_json)
        db.session.add(new_event)
        db.session.commit()

    yield new_event_json

    # Remove the region from the database at the end of the test if it still exists
    with app.app_context():
        event_exists = db.session.query(exists().where(Event.id == '33')).scalar()
        if event_exists:
            db.session.delete(new_event)
            db.session.commit()


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
