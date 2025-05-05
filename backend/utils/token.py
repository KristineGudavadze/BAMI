import jwt
import datetime

SECRET_KEY = 'your-secret-key'

ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)


def generate_tokens(user_id):
    now = datetime.datetime.utcnow()

    access_payload = {
        'user_id': user_id,
        'type': 'access',
        'exp': now + ACCESS_TOKEN_EXPIRES
    }
    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': now + REFRESH_TOKEN_EXPIRES
    }

    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm='HS256')

    return access_token, refresh_token


def verify_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != 'access':
            return None
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def verify_refresh_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != 'refresh':
            return None
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
