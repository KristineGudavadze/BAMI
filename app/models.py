# app/models.py
from app.extensions import db
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(100), unique=True)
    display_name = db.Column(db.String(100))
    genres = db.Column(db.String(500))
    top_artists = db.Column(JSON)
    top_genres = db.Column(JSON)
    recent_tracks = db.Column(JSON)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    matched_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
