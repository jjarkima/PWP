import json
import utils
#from datetime import datetime
from flask import Flask, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask_restful import Api, Resource
from jsonschema import validate, ValidationError
from utils import MasonBuilder, create_error_response
from utils import MASON, LINK_RELATIONS_URL, ERROR_PROFILE
from utils import TOPIC_PROFILE, MESSAGE_PROFILE, USER_PROFILE

app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)

from models import *#Topic, Message, User

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@app.route("/api/")
def entry_point():
    """
    Entry point
    """
    body = MasonBuilder()
    body.add_namespace("board", "/api/")
    body.add_control("board:topics-all", "/api/topics/")
    return Response(json.dumps(body), mimetype=MASON)


class BoardBuilder(MasonBuilder):
    """
    BoardBuilder created from MasonBuilder
    """
    @staticmethod
    def topic_schema():
        schema = {
            "type": "object",
            "required": ["id", "header", "message", "time", "user_id"]
        }
        props = schema["properties"] = {}
        props ["id"] = {
            "description": "topic id",
            "type": "integer"
        }
        props ["header"] = {
            "description": "header",
            "type": "string"
        }
        props ["message"] = {
            "description": "message",
            "type": "string"
        }
        props ["time"] = {
            "description": "time",
            "type": "string"
        }
        props ["user_id"] = {
            "description": "user id",
            "type": "integer"
        }
        return schema

    @staticmethod
    def message_schema():
        schema = {
            "type": "object",
            "required": ["id", "parent_topic_id", "message", "time", "user_id"]
        }
        props = schema["properties"] = {}
        props ["id"] = {
            "description": "id",
            "type": "integer"
        }
        props ["parent_topic_id"] = {
            "description": "parent topic id",
            "type": "integer"
        }
        props ["message"] = {
            "description": "message",
            "type": "string"
        }
        props ["time"] = {
            "description": "time",
            "type": "string"
        }
        props ["user_id"] = {
            "description": "user id",
            "type": "integer"
        }
        return schema

    @staticmethod
    def user_schema():
        schema = {
            "type": "object",
            "required": ["id", "username", "password"]
        }
        props = schema["properties"] = {}
        props ["id"] = {
            "description": "id",
            "type": "integer"
        }
        props ["username"] = {
            "description": "user name",
            "type": "string"
        }
        props ["password"] = {
            "description": "password",
            "type": "string"
        }
        return schema

    def add_control_all_topics(self):
        """
        Control to all topics
        """
        self.add_control(
            "board:topics-all",
            "/api/topics/",
            method="GET",
            encoding="json",
            title="Add control to all topics",
            schema=self.topic_schema()
            )

    def add_control_add_topic(self):
        """
        Control to add topic
        """
        self.add_control(
            "board:add-topic",
            api.url_for(TopicCollection),
            method="POST",
            encoding="json",
            title="Add a new topic",
            schema=self.topic_schema()
        )

    def add_control_add_message(self):
        """
        Control to add message
        """
        self.add_control(
            "board:add-message",
            api.url_for(MessageCollection),
            method="POST",
            encoding="json",
            title="Add new message",
            schema=self.message_schema()
        )

    def add_control_add_user(self):
        """
        Control to add user
        """
        self.add_control(
            "board:add-user",
            api.url_for(UserCollection),
            method="POST",
            encoding="json",
            title="Add new user",
            schema=self.user_schema()
        )

    def add_control_delete_topic(self, id):
        """
        Control to delete topic
        """
        self.add_control(
            "board:delete",
            api.url_for(TopicItem, id=id),
            method="DELETE",
            title="Delete this topic"
        )

    def add_control_delete_message(self, id):
        """
        Control to delete message
        """
        self.add_control(
            "board:delete",
            api.url_for(MessageItem, id=id),
            method="DELETE",
            title="Delete this message"
        )

    def add_control_delete_user(self, name):
        """
        Control to delete user
        """
        self.add_control(
            "board:delete",
            api.url_for(UserItem, username=name),
            method="DELETE",
            title="Delete user"
        )

    def add_control_edit_topic(self, id):
        """
        Control to edit topic
        """
        self.add_control(
            "edit",
            api.url_for(TopicItem, id=id),
            method="PUT",
            encoding="json",
            title="Edit this topic",
            schema=self.topic_schema()
        )

    def add_control_edit_message(self, id):
        """
        Control to edit message
        """
        self.add_control(
            "edit",
            api.url_for(MessageItem, id=id),
            method="PUT",
            encoding="json",
            title="Edit this message",
            schema=self.message_schema()
        )

class TopicCollection (Resource):
    """
    Resource for all topics in collection. Function GET gets all matches in collection
    and POST adds a new topic to collection
    """
    def get(self):
        """
        GET method to get all topics from the collection
        """
        body = BoardBuilder()

        body.add_namespace("board", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(TopicCollection))
        body.add_control_add_topic()
        body["items"] = []
        for db_topicid in Topic.query.all(): #slee iha skeidaa pitää tsiigaa
            item = BoardBuilder(
                #id = db_topicid.id,
                header = db_topicid.header,
                message = db_topicid.message,
                time = db_topicid.time,
                user_id = db_topicid.user_id
            )
            item.add_control("self", api.url_for(TopicItem, id=db_topicid.id)) #should work now juu ei oikeesti
            item.add_control("profile", TOPIC_PROFILE) # tää tekee slee jotai
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        """
        POST method adds new topic to collection
        """
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Request must be JSON")

        try:
            validate(request.json, BoardBuilder.topic_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        new_topic = Topic(
            #id=request.json["id"],
            header=request.json["header"],
            message=request.json["message"],
            time=request.json["time"],
            user_id=request.json["user_id"]
        )

        try:
            db.session.add(new_topic)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists", "Topic already inserted")

        return Response(status=201, headers={"Location": api.url_for(TopicItem, id=new_topic.id)})

class TopicItem (Resource):
    """
    Resource for single TopicItem. Function GET gets a single topic, PUT edits a single topic
    and DELETE deletes a topic.
    """

    def get(self, id):
        """
        GET method gets a single topic
        """
        db_topicid = Topic.query.filter_by(id=id).first()
        if db_topicid is None:
            return create_error_response(404, "Not found", "No topic was found with id {}".format(id))

        body = BoardBuilder(
            id=db_topicid.id,
            header=db_topicid.header,
            message=db_topicid.message,
            time=db_topicid.time,
            user_id=db_topicid.user_id
        )

        body.add_namespace("board", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(MatchItem, id=id))
        body.add_control("profile", TOPIC_PROFILE)
        body.add_control("collection", api.url_for(TopicCollection))
        body.add_control_delete_topic(id)
        body.add_control_edit_topic(id)

        return Response(json.dumps(body), status=200, mimetype=MASON)

    def put(self, id):
        """
        PUT method edits a single topic
        """
        db_topicid = Topic.query.filter_by(id=id).first()
        if db_topicid is None:
            return create_error_response(404, "Not found", "No topic was found with id {}".format(id))

        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, BoardBuilder.match_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))


        #db_topicid.id=request.json["id"]
        db_topicid.header=request.json["header"]
        db_topicid.message=request.json["message"]
        db_topicid.time=request.json["time"]
        db_topicid.user_id=request.json["user_id"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists", "Topic with id '{}' already exists".format(request.json["id"]))

        return Response(status=204)

    def delete(self, id):
        """
        DELETE method deletes a single topic
        """
        db_topicid = Topic.query.filter_by(id=id).first()
        if db_topicid is None:
            return create_error_response(404, "Not found", "No topic was found with id {}".format(id))

        db.session.delete(db_topicid)
        db.session.commit()

        return Response(status=204)

class MessageCollection (Resource):
    """
    Resource for MessageCollection. Function GET gets all the messages in collection
    and POST adds a new message to collection.
    """
    def get(self):
        """
        GET method gets all the messages from MessageCollection
        """
        body = BoardBuilder()

        body.add_namespace("board", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(MessageCollection))
        body.add_control_add_message()
        body["items"] = []
        for db_messageid in Message.query.all():
            item = BoardBuilder(
                id=db_messageid.id,
                parent_topic_id=db_messageid.parent_topic.id,
                message=db_messageid.message,
                time=db_messageid.time,
                user_id=db_messageid.user_id
            )
            item.add_control("self", api.url_for(MessageCollection))
            item.add_control("profile", MESSAGE_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), status=200, mimetype=MASON)

    def post(self):
        """
        POST method adds a new message to collection
        """
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, BoardBuilder.message_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        new_message = Message(
            id=request.json["id"],
            parent_topic_id=request.json["parent_topic_id"],
            message=request.json["message"],
            time=request.json["time"],
            user_id=request.json["user_id"]
        )

        try:
            db.session.add(new_message)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists", "message with id '{}' already exists".format(request.json["id"]))

        return Response(status=201, headers={"Location": api.url_for(MessageItem, id=request.json["id"])})

class MessageItem (Resource):
    """
    Resource for MessageItem. Function GET gets a single message, PUT edits a message
    and DELETE deletes a message.
    """
    def get(self, id):
        """
        GET method gets a single message
        """
        db_messageid = Message.query.filter_by(id=id).first()
        if db_messageid is None:
            return create_error_response(404, "Not found", "No message was found with id {}".format(id))

        body = BoardBuilder(
            id=db_messageid.id,
            parent_topic_id=db_messageid.parent_topic.id,
            message=db_messageid.message,
            time=db_messageid.time,
            user_id=db_messageid.user_id
        )

        body.add_namespace("board", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(MessageItem, id=id))
        body.add_control("profile", MESSAGE_PROFILE)
        body.add_control("collection", api.url_for(MessageCollection))
        body.add_control_delete_message(id)
        body.add_control_edit_message(id)

        return Response(json.dumps(body), status=200, mimetype=MASON)

    def put(self, id):
        """
        PUT method edits a single message
        """
        db_messageid = Message.query.filter_by(id=id).first()
        if db_messageid is None:
            return create_error_response(404, "Not found", "No message was found with id {}".format(id))

        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, BoardBuilder.message_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_messageid.id = request.json["id"],
        db_messageid.parent_topic_id = request.json["parent_topic_id"],
        db_messageid.message = request.json["message"],
        db_messageid.time = request.json["time"],
        db_messageid.user_id = request.json["user_id"]

        try:
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists", "Message with id '{}' already exists".format(request.json["id"]))

        return Response(status=204)

    def delete(self, id):
        """
        DELETE method deletes a single message
        """
        db_messageid = Message.query.filter_by(id=id).first()
        if db_messageid is None:
            return create_error_response(404, "Not found", "No message was found with id {}".format(id))

        db.session.delete(db_messageid)
        db.session.commit()

        return Response(status=204)

class UserCollection (Resource):
    """
    Resource for UserCollection. Function GET gets all the users in collection
    and POST adds a new user to collection.
    """
    def get(self):
        """
        GET method gets all the users from collection
        """
        body = BoardBuilder()

        body.add_namespace("board", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(UserCollection))
        body.add_control_add_user()
        body["items"] = []
        for db_userid in User.query.all():
            item = BoardBuilder(
                #id=db_userid.id,
                username=db_userid.username,
                password=db_userid.password
            )
            item.add_control("self", api.url_for(UserCollection))
            item.add_control("profile", USER_PROFILE)
            body["items"].append(item)

        return Response(json.dumps(body), status=200, mimetype=MASON)

    def post(self):
        """
        POST method adds a new user to collection
        """
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, BoardBuilder.user_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        new_user = User(
            #id=request.json["id"],
            username=request.json["username"],
            password=request.json["password"]
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists", "User with name '{}' already exists".format(request.json["username"]))

        return Response(status=201, headers={"Location": api.url_for(UserItem, username=request.json["username"])})

class UserItem (Resource):
    """
    Resource for single UserItem. Function GET gets a user, PUT edits a user
    and DELETE deletes a user.
    """
    def get(self, name):
        """
        GET method gets a single user
        """
        db_userid = User.query.filter_by(username=name).first()
        if db_userid is None:
            return create_error_response(404, "Not found", "No user was found with name {}".format(name))

        body = BoardBuilder(
            #id=db_userid.id,
            username=db_userid.username,
            password=db_userid.password
        )

        body.add_namespace("board", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(UserItem, username=name))
        body.add_control("profile", USER_PROFILE)
        body.add_control("collection", api.url_for(UserCollection))
        body.add_control_delete_user(name)

        return Response(json.dumps(body), status=200, mimetype=MASON)

    def delete(self, name):
        """
        DELETE method deletes a user
        """
        db_userid = User.query.filter_by(username=name).first()
        if db_userid is None:
            return create_error_response(404, "Not found", "No user was found with name {}".format(name))

        db.session.delete(db_userid)
        db.session.commit()

        return Response(status=204)

api.add_resource(TopicCollection, "/api/topics/")
api.add_resource(TopicItem, "/api/topics/<id>/")
api.add_resource(MessageCollection, "/api/messages/")
api.add_resource(MessageItem, "/api/messages/<id>/")
api.add_resource(UserCollection, "/api/users/")
api.add_resource(UserItem, "/api/users/<username>/")

@app.route(LINK_RELATIONS_URL)
def send_link_relations():
    return "link relations"

@app.route("/profiles/<profile>/")
def send_profile(profile):
    return "you requests {} profile".format(profile)
@app.route("/admin/")
def admin_site():
    return app.send_static_file("html/admin.html")


# Main function to create database
#def main():
    #pandaDb = pwpDatabase.PWPDatabase(pwpDatabase.SQLITE, dbname='pandaDB.sqlite')

    #Phase 1
    # Create Tables
    #pandaDb.create_db_tables()

    #Phase 2
    #Print all data
    #pandaDb.print_all_data(pwpDatabase.USERS)
    #pandaDb.print_all_data(pwpDatabase.TOPICS)
    #pandaDb.print_all_data(pwpDatabase.MESSAGES)

    #Phase 3
    #Test retreival
    #pandaDb.retrieve_query() # simple query

    #Phase 4
    #Test Insert
    #pandaDb.insert_query() # insert data

    #Phase 5
    #Test Update
    #pandaDb.update_query() # update data

    #Phase 6
    #Test Delete
    #pandaDb.delete_query() # delete data

    #from example_data import db_load_example_data
    #db_load_example_data(app, db)

    #print("pwp.py main ran.")


# Run the program
#if __name__ == "__main__": main()
