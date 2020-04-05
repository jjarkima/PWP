#import json
#from flask import Flask, request, abort
#from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event

from app import db
#from flask_restful import Api, Resource

#app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#db = SQLAlchemy(app)
#api = Api(app)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(128), nullable=False)
    message = db.Column(db.String(360), nullable=False)
    date = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(360), nullable=False)
    date = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    parent_topic_id = db.Column(db.Integer, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
