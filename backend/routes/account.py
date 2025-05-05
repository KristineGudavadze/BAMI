from collections import Counter
import requests
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from config import CLIENT_ID, REDIRECT_URI, CLIENT_SECRET
from extensions import login_manager, db
from models.account import User

from utils.token import generate_tokens, verify_refresh_token

routes = Blueprint('account', __name__)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    service = data.get('service')

    if not service:
        return jsonify({"error": "Service type not provided"}), 400

    if service == 'spotify':
        scope = "user-read-private user-read-email user-top-read user-read-recently-played"
        auth_url = (
            "https://accounts.spotify.com/authorize"
            "?response_type=code"
            f"&client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&scope={scope.replace(' ', '%20')}"
        )
        return jsonify({"auth_url": auth_url})

    elif service == 'apple':
        return jsonify({"message": "Apple Music login not yet implemented."}), 501

    else:
        return jsonify({"error": "Unsupported service"}), 400


@routes.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Authorization code not provided"}), 400

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(token_url, data=payload)
    token_data = response.json()
    access_token = token_data.get('access_token')

    print("Spotify Access Token:", access_token)

    if not access_token:
        return jsonify({"error": "Failed to get access token from Spotify"}), 400

    # Get user info
    user_info = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    user = User.query.filter_by(spotify_id=user_info['id']).first()
    if not user:
        user = User(
            spotify_id=user_info['id'],
            display_name=user_info.get('display_name'),
            genres=user_info.get('genres', '')
        )
        db.session.add(user)
        db.session.commit()

    top_artists = requests.get(
        'https://api.spotify.com/v1/me/top/artists?limit=10',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    top_genres = []
    for artist in top_artists.get('items', []):
        top_genres.extend(artist.get('genres', []))
    genre_counts = Counter(top_genres)
    top_genres = [genre for genre, _ in genre_counts.most_common(5)]

    recent_tracks = requests.get(
        'https://api.spotify.com/v1/me/player/recently-played?limit=10',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    user.top_artists = [artist['name'] for artist in top_artists.get('items', [])]
    user.top_genres = top_genres
    user.recent_tracks = [track['track']['name'] for track in recent_tracks.get('items', [])]
    db.session.commit()

    access, refresh = generate_tokens(user.id)
    return jsonify({
        "access": access,
        "refresh": refresh
    })


@routes.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh')
    user_id = verify_refresh_token(refresh_token)

    if not user_id:
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    access, _ = generate_tokens(user_id)
    return jsonify({"access": access})


@routes.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify(current_user.serialize())

