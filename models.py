from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    serial = db.Column(db.String(64), nullable=True)
    imei = db.Column(db.String(15), nullable=True)
    join_datetime = db.Column(db.DateTime, server_default=db.func.now())

class Location(db.Model):
    __tablename__ = 'location'

    user = db.Column(db.String(32), primary_key=True)
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)