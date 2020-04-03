import json
import os
import pytest
import tempfile
#import time
from jsonschema import validate
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.engine import Engine
from sqlalchemy import event

from pwp import app as pwp
#from pwp import db
from models import Topic, Message, User, db
import utils


import datetime
from datetime import datetime
aika = datetime.now()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    pwp.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    pwp.config["TESTING"] = True

    db.create_all()
    _populate_db()

    yield pwp.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


def _populate_db():
    """
    Pre-populate database with 2 topics, 2 messages and 2 users
    """
    topic1 = Topic(
        #id=1,
        header="Pervo",
        message="prv o prvo",
        time=aika,
        user_id=1,
    )

    topic2 = Topic(
        #id=2,
        header="Pervo",
        message="prv o prvo",
        time=aika,
        user_id=2,
    )

    message1 = Message(
        #id=1,
        message="asdasdasdasd",
        time=aika,
        user_id=1,
        parent_topic_id=1
    )

    message2 = Message(
        #id=2,
        message="asdasdasdasd",
        time=aika,
        user_id=2,
        parent_topic_id=2
    )

    user1 = User(
        #id=1,
        username="paavo",
        password="asd"
    )

    user2 = User(
        #id=2,
        username="paavo-pertti",
        password="asd123"
    )

    db.session.add(topic1)
    db.session.add(topic2)

    db.session.add(message1)
    db.session.add(message2)

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()


def _get_topic_json():
	return {
		"id":1,
		"header": "asdasd",
		"message": "asdasdasd",
		"time": aika,
		"user_id": 1
    }

def _get_message_json():
	return {
		"id": 1,
    	"message": "asdasdasdasd",
    	"time": aika,
    	"user_id": 1,
    	"parent_topic_id": 1
    }

def _get_user_json():
	return {
    	"id": 1,
    	"username": "paavo",
    	"password": "asd"
    }


def _check_namespace(client, response):
    """
    Checks that the "board" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """

    ns_href = response["@namespaces"]["board"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200


def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200


def _check_control_post_method_topic(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_topic_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


def _check_control_post_method_user(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_user_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


def _check_control_post_method_message(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_message_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204


def _check_control_put_method_topic(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_topic_json()
    body["id"] = obj["id"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204


"""def _check_control_put_method_user(ctrl, client, obj):
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_user_json()
    body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204"""


def _check_control_put_method_message(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_message_json()
    body["id"] = obj["id"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204


class TestTopicCollection(object):
    RESOURCE_URL = "/api/topics/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method_topic("board:add-topic", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            assert "id" in item
            assert "header" in item
            assert "message" in item
            assert "time" in item
            assert "user_id" in item

    def test_post(self, client):
        valid = _get_topic_json()

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        id = body["items"][-1]["id"]
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + str(id) + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["id"] == 1
        assert body["header"] == "asdasd"
        assert body["message"] == "asdasdasd"
        assert body["time"] == aika
        assert body["user_id"] == 1

        # test with wrong content type(must be json)
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove title field for 400
        valid.pop("id")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestMessageItem(object):
    RESOURCE_URL = "/api/messages/1/"
    INVALID_URL = "/api/messages/x/"
    MODIFIED_URL = "/api/messages/2/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["id"] == "1"
        assert body["message"] == "asdasdasdasd"
        assert body["time"] == aika
        assert body["user_id"] == 1
        assert body["parent_topic_id"] == 1
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method_message("edit", client, body)
        _check_control_delete_method("board:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        valid = _get_topic_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test with another topic's id
        valid["id"] = 2
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test with valid (only change id)
        valid["id"] = 1
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # remove field for 400
        valid.pop("header")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_topic_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["asdasdasd"] == valid["asdasdasd"]

    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestUserCollection(object):
    RESOURCE_URL = "/api/users/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method_user("board:add-user", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            assert "username" in item
            assert "password" in item

    def test_post(self, client):
        valid = _get_user_json()

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        id = body["items"][-1]["username"]
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + str(id) + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == "paavo"
        assert body["password"] == "asd"

        # test with wrong content type(must be json)
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove title field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestUserItem(object):
    RESOURCE_URL = "/api/users/paavo/"
    INVALID_URL = "/api/users/arghh/"
    MODIFIED_URL = "/api/users/paavo-pertti/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["username"] == "paavo"
        assert body["password"] == "asd"
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method_user("edit", client, body)
        _check_control_delete_method("board:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        valid = _get_user_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test with another users's name
        valid["username"] = "paavo-pertti"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test with valid (only change name)
        valid["username"] = "paavo"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # remove field for 400
        valid.pop("password")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_user_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["password"] == valid["password"]

    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestMessageCollection(object):
    RESOURCE_URL = "/api/messages/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)

        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        # _check_control_post_method_throw("board:add-message", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            assert "id" in item
            assert "message" in item
            assert "time" in item
            assert "user_id" in item
            assert "parent_topic_id" in item

    def test_post(self, client):
        valid = _get_message_json()
        # test with wrong content type(must be json)
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove msg field for 400
        valid.pop("time")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestMessageItem(object):
    RESOURCE_URL = "/api/messages/1/"
    INVALID_URL = "/api/messages/agghh/"
    MODIFIED_URL = "/api/messages/2/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["id"] == 1
        assert body["message"] == "asdasdasdasd"
        assert body["time"] == aika
        assert body["user_id"] == 1
        assert body["parent_topic_id"] == 1
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method_message("edit", client, body)
        _check_control_delete_method("board:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        valid = _get_message_json()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test with another id
        valid["id"] = 2
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        # remove field for 400
        valid.pop("time")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_message_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        #print(valid["match_id"])
        assert body["id"] == valid["id"]

    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
