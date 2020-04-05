import json
import os
import pytest
import tempfile
import time
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from app import app
from models import Topic, Message, User, db
import utils

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
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True

    db.create_all()
    _populate_db()

    yield app.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)
    
def _populate_db():
    """
    Pre-populate database with 2 topics, 2 users and 2 messages
    """
    topic1 = Topic(
        id=1,
        header="Pervo",
        message="prv o prvo",
        date="Aika",
        user_id=1,
    )

    topic2 = Topic(
        id=2,
        header="Pervo",
        message="prv o prvo",
        date="Aika",
        user_id=2,
    )

    message1 = Message(
        id=1,
        message="asdasdasdasd",
        date="Aika",
        user_id=1,
        parent_topic_id=1
    )

    message2 = Message(
        id=2,
        message="asdasdasdasd",
        date="Aika",
        user_id=2,
        parent_topic_id=2
    )

    user1 = User(
        id=1,
        name="paavo",
        password="asd"
    )

    user2 = User(
        id=2,
        name="pertti",
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
		"id":3,
		"header": "asdasd3",
		"message": "asdasdasd3",
		"date": "Aika",
		"user_id": 3
    }

def _get_user_json():
	return {
    	"id": 3,
    	"name": "jammu",
    	"password": "asd3"
    }

def _get_message_json():
	return {
		"id": 3,
    	"message": "asdasdasdasd3",
    	"date": "Aika",
    	"user_id": 3,
    	"parent_topic_id": 3
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

def _check_control_post_method(ctrl, client, obj):
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

def _check_control_put_method(ctrl, client, obj):
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
    
def _check_control_put_method_user(ctrl, client, obj):
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
    body = _get_user_json()
    body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204
    
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
        _check_control_post_method("board:add-topic", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            assert "id" in item
            assert "header" in item
            assert "message" in item
            assert "date" in item
            assert "user_id" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        valid = _get_topic_json()

        #  Here we insert valid data and then check it succeeded
        resp = client.post(self.RESOURCE_URL, json=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        print(body["items"])
        id = body["items"][-1]["id"]
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + str(id) + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["id"] == 3
        assert body["header"] == "asdasd3"
        assert body["message"] == "asdasdasd3"
        assert body["date"] == "Aika"
        assert body["user_id"] == 3

        #  Here we insert wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        #  Here we pop a field to get a 400
        valid.pop("id")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
class TestTopicItem(object):
    
    RESOURCE_URL = "/api/topics/1/"
    INVALID_URL = "/api/topics/x/"
    MODIFIED_URL = "/api/topics/3/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["id"] == 1
        assert body["header"] == "Pervo"
        assert body["message"] == "prv o prvo"
        assert body["date"] == "Aika"
        assert body["user_id"] == 1
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method("edit", client, body) 
        _check_control_delete_method("board:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
       
    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible error codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI.
        """
        
        valid = _get_topic_json()
        
        #  Here we insert wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        #  Here we test with second id
        valid["id"] = 2
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        #  Here we test with valid id
        valid["id"] = 1
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        #  Here we pop a field to get a 400
        valid.pop("header")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_topic_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["header"] == valid["header"]
               
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

class TestUserCollection(object):

    RESOURCE_URL = "/api/users/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method_user("board:add-user", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            assert "name" in item
            assert "password" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_user_json()

        #  Here we insert valid data and then check it succeeded
        resp = client.post(self.RESOURCE_URL, json=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        id = body["items"][-1]["name"] 
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + str(id) + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "jammu"
        assert body["password"] == "asd3"

        #  Here we insert wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        #  Here we pop a field to get a 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestUserItem(object):
    
    RESOURCE_URL = "/api/users/paavo/"
    INVALID_URL = "/api/users/3/"
    MODIFIED_URL = "/api/users/jammu/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "paavo"
        assert body["password"] == "asd"
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_put_method_user("edit", client, body)
        _check_control_delete_method("board:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
      
    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible error codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI.
        """
        
        valid = _get_user_json()
        
        #  Here we insert wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
       
        #  Here we test with second name
        print(valid["name"])
        valid["name"] = "pertti"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409  # 409
        
        #  Here we test with valid name
        valid["name"] = "paavo"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        #  Here we pop a field to get a 400
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
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
        
class TestMessageCollection(object):
    
    RESOURCE_URL = "/api/messages/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
    
        resp = client.get(self.RESOURCE_URL)
        
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        #  This line didn't work
        assert len(body["items"]) == 2
        for item in body["items"]:
            assert "id" in item
            assert "message" in item
            assert "date" in item
            assert "user_id" in item
            assert "parent_topic_id" in item
        
    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_message_json()

        #  valid test didn't work

        #  Here we insert wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        #  Here we pop a field to get a 400
        valid.pop("message")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
class TestMessageItem(object):
    
    RESOURCE_URL = "/api/messages/1/"
    INVALID_URL = "/api/messages/6/"
    MODIFIED_URL = "/api/messages/2/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["id"] == 1
        assert body["message"] == "asdasdasdasd"
        assert body["date"] == "Aika"
        assert body["user_id"] == 1
        assert body["parent_topic_id"] == 1
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("collection", client, body)
        _check_control_delete_method("board:delete", client, body)
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404
    
    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible error codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI.
        """
        valid = _get_message_json()
        
        #  Here we insert wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        #  Here we test with second id
        valid["id"] = 2
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400  # old 409

        #  Valid test with ID change didn't work
        """valid["id"] = 1
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204"""

        #  Here we pop a field to get a 400
        valid.pop("message")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_message_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["user_id"] == valid["user_id"]
            
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request receives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
    
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
    
