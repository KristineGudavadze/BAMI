from extensions import db
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON


class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(100), unique=True)
    display_name = db.Column(db.String(100))
    genres = db.Column(db.String(500))
    top_artists = db.Column(JSON)
    top_genres = db.Column(JSON)
    recent_tracks = db.Column(JSON)

    def serialize(self):
        return {
            'id': self.id,
            'spotify_id': self.spotify_id,
            'display_name': self.display_name,
            'genres': self.genres,
            'top_artists': self.top_artists,
            'top_genres': self.top_genres,
            'recent_tracks': self.recent_tracks
        }
