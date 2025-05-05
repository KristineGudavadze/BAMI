from flask import Blueprint, jsonify, request
from models.message import Message
from extensions import db
from flask_login import login_required, current_user

routes = Blueprint('message', __name__)


@routes.route('/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    new_message = Message(
        content=data['content'],
        sender_id=current_user.id,
        receiver_id=data['receiver_id']
    )
    db.session.add(new_message)
    db.session.commit()
    return jsonify(new_message.serialize())


@routes.route('/list/<int:user_id>', methods=['GET'])
@login_required
def list_messages(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    return jsonify([message.serialize() for message in messages])
