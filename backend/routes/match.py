from flask import Blueprint, jsonify
from models.match import Match
from models.account import User
from flask_login import login_required, current_user

routes = Blueprint('match', __name__)


@routes.route('/list', methods=['GET'])
@login_required
def match_list():
    matches = Match.query.filter_by(user_id=current_user.id).all()
    return jsonify([match.serialize() for match in matches])


@routes.route('/find', methods=['GET'])
@login_required
def find_matches():
    matches = User.query.filter(User.id != current_user.id).all()
    match_data = [{'user': match.serialize()} for match in matches]
    return jsonify(match_data)
