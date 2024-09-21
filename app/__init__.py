from flask import Flask
from .routes import authentication

def create_app():
    app = Flask(__name__)

    # Register blueprints for modular routes
    app.register_blueprint(authentication.bp, url_prefix='/users')
    return app
