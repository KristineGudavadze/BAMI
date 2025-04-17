from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Match, Message
from app.extensions import db, login_manager
import requests
import os
from collections import Counter
from datetime import datetime

routes = Blueprint('routes', __name__)

# Spotify credentials (you can load these from environment variables)
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'your_client_id_here')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'your_client_secret_here')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/callback')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@routes.route('/')
def home():
    return render_template('home.html')

# Login route
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        service = request.form.get('service')
        if service == 'spotify':
            scope = "user-read-private user-read-email user-top-read user-read-recently-played"
            auth_url = (
                "https://accounts.spotify.com/authorize"
                f"?response_type=code&client_id={CLIENT_ID}"
                f"&redirect_uri={REDIRECT_URI}"
                f"&scope={scope.replace(' ', '%20')}"
            )
            return redirect(auth_url)
        elif service == 'apple':
            return "Apple Music login not yet implemented."
    return render_template('login.html')

# OAuth callback route
@routes.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
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

        # Get user info from Spotify
        user_info_response = requests.get(
            'https://api.spotify.com/v1/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_info = user_info_response.json()

        user = User.query.filter_by(spotify_id=user_info['id']).first()
        if not user:
            user = User(
                spotify_id=user_info['id'],
                display_name=user_info.get('display_name'),
                genres=user_info.get('genres', '')
            )
            db.session.add(user)
            db.session.commit()

        # Fetch user's top artists
        top_artists_response = requests.get(
            'https://api.spotify.com/v1/me/top/artists?limit=10',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        top_artists = top_artists_response.json()

        # Extract top genres
        top_genres = []
        for artist in top_artists['items']:
            top_genres.extend(artist['genres'])
        top_genres_count = Counter(top_genres)
        top_genres = [genre for genre, _ in top_genres_count.most_common(5)]

        # Fetch recent tracks
        recent_tracks_response = requests.get(
            'https://api.spotify.com/v1/me/player/recently-played?limit=10',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        recent_tracks = recent_tracks_response.json()

        # Update user
        user.top_artists = [artist['name'] for artist in top_artists['items']]
        user.top_genres = top_genres
        user.recent_tracks = [track['track']['name'] for track in recent_tracks['items']]
        db.session.commit()

        login_user(user)
        return redirect(url_for('routes.account'))

    return "Authentication failed"

# Account page
@routes.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)

# Match page
@routes.route('/match')
@login_required
def match():
    matches = User.query.filter(User.id != current_user.id).all()
    for match in matches:
        match.similarity = calculate_similarity(current_user, match)
    return render_template('matching.html', matches=matches)

def calculate_similarity(user1, user2):
    user1_genres = set(user1.top_genres)
    user2_genres = set(user2.top_genres)
    common_genres = user1_genres.intersection(user2_genres)
    return len(common_genres)

# Connect to a user
@routes.route('/connect/<int:user_id>', methods=['POST'])
@login_required
def connect(user_id):
    matched_user = User.query.get_or_404(user_id)
    if matched_user:
        match = Match(user_id=current_user.id, matched_user_id=matched_user.id)
        db.session.add(match)
        db.session.commit()
    return redirect(url_for('routes.match'))

# Skip a match
@routes.route('/skip/<int:user_id>', methods=['POST'])
@login_required
def skip(user_id):
    return redirect(url_for('routes.match'))

# Chat page
@routes.route('/chat/<int:matched_user_id>', methods=['GET', 'POST'])
@login_required
def chat(matched_user_id):
    matched_user = User.query.get_or_404(matched_user_id)
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == matched_user_id)) |
        ((Message.sender_id == matched_user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    if request.method == 'POST':
        message_content = request.form.get('message')
        if message_content:
            new_message = Message(
                sender_id=current_user.id,
                receiver_id=matched_user_id,
                content=message_content
            )
            db.session.add(new_message)
            db.session.commit()
        return redirect(url_for('routes.chat', matched_user_id=matched_user_id))

    return render_template('chat.html', matched_user=matched_user, messages=messages)

# Logout
@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))
