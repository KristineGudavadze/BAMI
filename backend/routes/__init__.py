from routes.account import routes as account_bp
from routes.match import routes as match_bp
from routes.message import routes as message_bp


def register_blueprints(app):
    app.register_blueprint(account_bp, url_prefix="/account")
    app.register_blueprint(match_bp, url_prefix="/match")
    app.register_blueprint(message_bp, url_prefix="/message")
