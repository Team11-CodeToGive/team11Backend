from flask import Flask
from .routes import authentication, community

def create_app():
    app = Flask(__name__)

    # Register blueprints for modular routes
    app.register_blueprint(authentication.bp, url_prefix='/users')
    app.register_blueprint(community.bp, url_prefix = '/community')

    return app
