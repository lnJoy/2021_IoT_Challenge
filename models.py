from flask_sqlalchemy import SQLAlchemy

import sqlite3
from flask import g

from app import app

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    serial = db.Column(db.String(64), nullable=True)
    imei = db.Column(db.String(15), nullable=True)
    join_datetime = db.Column(db.DateTime, server_default=db.func.now())

class Location(db.Model):
    __tablename__ = 'location'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    jwt = db.Column(db.String(1024), nullable=True)
    latitude = db.Column(db.Integer, nullable=True)
    longitude = db.Column(db.Integer, nullable=True)

# CREATE TABLE user_info(id INTEGER PRIMARY KEY AUTOINCREMENT, serial CHAR(64) NOT NULL, key CHAR(15) NOT NULL, firebase CHAR(1024) NOT NULL, create_datetime DATETIME DEFAULT (DATETIME('now', 'localtime')));
# CREATE TABLE location(id INTEGER PRIMARY KEY AUTOINCREMENT, jwt VARCHAR(512) NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL, last_timestamp DATETIME DEFAULT (DATETIME('now', 'localtime')));