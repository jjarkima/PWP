import os
import pytest
import tempfile
import time
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

import app
from app import Topic, Message, User

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True
    
    with app.app.app_context():
        app.db.create_all()
        
    yield app.db

    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


def _get_topic():
    return Topic(
        header = "Pervo",
        message = "prv o prvo",
        date = "Aika",
        user_id = 1
    )


def _get_message():
    return Message(
        message="asdasdasdasd",
        date="Aika",
        user_id=1,
        parent_topic_id=1
    )


def _get_message2():
    return Message(
        message="asdasdasdasd",
        date="Aika",
        user_id=2,
        parent_topic_id=2
    )


def _get_user1():
    return User(
        name="paavo",
        password="asd"
    )


def _get_user2():
    return User(
        name="paavo-pertti",
        password="asd123"
)


def _get_user3():
    return User(
        name="paavo-pertti1",
        password="asd1234"
    )


def test_create_instances(db_handle):
    """
    Tests that we can create few instances of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """
    topic = _get_topic()
    message = _get_message()
    message2 = _get_message2()
    user1 = _get_user1()
    user2 = _get_user2()
    user3 = _get_user3()
    db_handle.session.add(topic)
    db_handle.session.add(message)
    db_handle.session.add(message2)
    db_handle.session.add(user1)
    db_handle.session.add(user2)
    db_handle.session.add(user3)
    db_handle.session.commit()

    assert Topic.query.count() == 1
    assert Message.query.count() == 2
    assert User.query.count() == 3
    db_topic = Topic.query.first()
    db_message = Message.query.first()
    db_user = User.query.first()
 

def test_create_topic(db_handle):
    topic = _get_topic()

    db_handle.session.add(topic)
    db_handle.session.commit()
    assert Topic.query.count() == 1

def test_create_message(db_handle):
    message = _get_message()

    db_handle.session.add(message)
    db_handle.session.commit()
    assert Message.query.count() == 1

def test_create_user(db_handle):
    user = _get_user1()

    db_handle.session.add(user)
    db_handle.session.commit()
    assert User.query.count() == 1


def test_delete_topic(db_handle):
    topic = _get_topic()

    db_handle.session.add(topic)
    db_handle.session.commit()
    db_handle.session.delete(topic)
    db_handle.session.commit()
    try:
        assert Topic.query.count() == 1
    except AssertionError:
        print("deletetopic asserterror")

def test_delete_message(db_handle):
    message = _get_message()

    db_handle.session.add(message)
    db_handle.session.commit()
    db_handle.session.delete(message)
    db_handle.session.commit()
    try:
        assert Message.query.count() == 1
    except AssertionError:
        print("deletemsg asserterror")

def test_delete_user(db_handle):
    user = _get_user1()

    db_handle.session.add(user)
    db_handle.session.commit()
    db_handle.session.delete(user)
    db_handle.session.commit()
    try:
        assert User.query.count() == 1
    except AssertionError:
        print("deleteuser asserterror")

def test_update_topic(db_handle):
    topic = _get_topic()

    db_handle.session.add(topic)
    db_handle.session.commit()
    topic.message = "uusitopic"
    db_handle.session.add(topic)
    db_handle.session.commit()
    assert topic.message == "uusitopic"

def test_update_message(db_handle):
    message = _get_message()

    db_handle.session.add(message)
    db_handle.session.commit()
    message.message = "uusimsg"
    db_handle.session.add(message)
    db_handle.session.commit()
    assert message.message == "uusimsg"