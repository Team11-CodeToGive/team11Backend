from flask import Flask
from .routes import authentication,event_comments

def create_app():
    app = Flask(__name__)

    # Register blueprints for modular routes
    app.register_blueprint(authentication.bp, url_prefix='/users')
    app.register_blueprint(event_comments.bp, url_prefix='/comments')
    return app
