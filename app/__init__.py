from flask import Flask
from .routes import authentication, community, event, eventRegistration
from .routes import authentication,event_comments
from .routes import authentication, community, image_upload

from .routes import authentication, community
from .routes import report
def create_app():
    app = Flask(__name__)

    # Register blueprints for modular routes
    app.register_blueprint(authentication.bp, url_prefix='/users')
    app.register_blueprint(event_comments.bp, url_prefix='/comments')
    app.register_blueprint(image_upload.bp, url_prefix='/image_upload')
    app.register_blueprint(community.bp, url_prefix = '/community')
    app.register_blueprint(event.bp, url_prefix = '/event')
    app.register_blueprint(report.bp, url_prefix='/report')
    app.register_blueprint(eventRegistration.bp, url_prefix = '/event_registration')




    return app
