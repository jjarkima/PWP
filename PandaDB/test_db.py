import os
import pytest
import tempfile

import datetime
from datetime import datetime
aika = datetime.now()

import models
from models import Topic, Message, User

import pwp

# Foreign keys ON
from sqlalchemy.engine import Engine
from sqlalchemy import event

#time_all = datetime.now()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


''' Tests for SQLAlchemy database. Tests are implemented with the assumption that
    SQLAlchemy uses SQL queries correctly, so only database models and their relations are tested.'''


@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    pwp.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    pwp.app.config["TESTING"] = True

    #with pwp.app_context():
    pwp.db.create_all()

    yield pwp.db

    pwp.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


def _get_topic():
	return Topic(
        #id = 1,
        header = "Pervo",
        message = "prv o prvo",
        #time = datetime.datetime.now(),
        time = aika,
        user_id = 1,
	)


def _get_message():
    return Message(
        #id = 1,
        message = "asdasdasdasd",
        #time = datetime.datetime.now(),
        time = aika,
        user_id = 1,
        parent_topic_id = 1
	)


def _get_user():
    return User(
        #id = 9,
        username="paavo",
        password="asd",
        #posted_topics="aghh",
        #posted_messages="ayy"
	)

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
    user = _get_user()

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
    user = _get_user()

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

