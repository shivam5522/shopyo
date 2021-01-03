"""
File conftest.py contains pytest fixtures that are used in numerous
test functions. Refer to https://docs.pytest.org/en/stable/fixture.html
for more details on pytest
"""
import json
import os


from flask import url_for


import pytest

from app import create_app
from shopyoapi.init import db as _db
from shopyoapi.uploads import add_setting
from modules.admin.models import User
from modules.settings.models import Settings

# from shopyoapi.cmd import initialise


# run in shopyo/shopyo
# python -m pytest . or python -m pytest -v


if os.path.exists("testing.db"):
    os.remove("testing.db")


@pytest.fixture(scope="session")
def new_user():
    """
    A pytest fixture that returns a user model object
    """
    user = User(email="admin3@domain.com")
    user.set_hash("pass")
    return user


@pytest.fixture(scope="session")
def test_client():
    """
    setups up and returns the flask testing app
    """
    flask_app = create_app("testing")

    # Create a test client using the Flask application configured for testing
    # we need this with block to be able to use application context
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope="session")
def db(test_client):
    """
    creates and returns the initial testing database
    """
    # Create the database and the database table
    _db.app = test_client
    _db.create_all()

    # Insert user data
    user1 = User(email="admin1@domain.com")
    user1.set_hash("pass")
    user2 = User(email="admin2@domain.com", is_admin=True)
    user2.set_hash("pass")
    _db.session.add(user1)
    _db.session.add(user2)

    # add the default settings
    with open("config.json", "r") as config:
        config = json.load(config)

    for name, value in config["settings"].items():
        s = Settings(setting=name, value=value)
        _db.session.add(s)

    # Commit the changes for the users
    _db.session.commit()

    yield _db  # this is where the testing happens!

    _db.drop_all()


@pytest.yield_fixture(scope="function", autouse=True)
def db_session(db):
    """
    Creates a new database session for a test. Note you must use this fixture
    if your test connects to db. Autouse is set to true which implies
    that the fixture will be setup before each test

    Here we not only support commit calls but also rollback calls in tests.
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    yield db  # this is where the testing happens!
    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture(scope="session")
def _db(init_database):
    return init_database


# Want TO USE THE BELOW CODE FOR LOGIN AND LOGOUT
# TO REMOVE REPEATED CODE FROM ALL TESTS. BUT
# CURRENTLY FAILING TO MAKE LOGIN WORK FROM OUTSIDE
# THE TEST FUNCTION

# @pytest.fixture
# def auth(test_client):
#     return AuthActions(test_client)


# class AuthActions(object):
#     def __init__(self, client):
#         self._client = client

#     def login(self, user):
#         return self._client.post(
#             url_for("login.login"),
#             data=dict(email="admin1@domain.com", password="pass"),
#             follow_redirects=True,
#         )

# def logout(self):
#     return self._client.get(
#         url_for("login.logout"), follow_redirects=True)
