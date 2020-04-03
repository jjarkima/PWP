#import json
#from flask import Flask, request, abort
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask_sqlalchemy import SQLAlchemy

#from pwp import db

db = SQLAlchemy()



#from flask_restful import Api, Resource

#app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#db = SQLAlchemy()
#api = Api(app)

class Topic(db.Model):
    #__tablename__ = 'Topic'
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(128), nullable=False)
    message = db.Column(db.String(360), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    """def __repr__(self):
        return "topicreturn"

    def __init__(self, header=None, message=None, time=None, user_id=None):
        self.header = header
        self.message = message
        self.time = time
        self.user_id = user_id"""

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(360), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    parent_topic_id = db.Column(db.Integer, nullable=False)

    """def __init__(self, message=None, time=None, user_id=None, parent_topic_id=None):
        self.message = message
        self.time = time
        self.user_id = user_id
        self.parent_topic_id = parent_topic_id"""

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)

    """def __init__(self, username=None, password=None):
        self.username = username
        self.password = password"""
