from flask import Blueprint

# Import the routes from each module
from .patients import patients_bp
from .rooms import rooms_bp
from .incidents import incidents_bp
from .notifications import notifications_bp

def create_routes(app):
    # Register the Blueprints with the Flask app
    app.register_blueprint(patients_bp, url_prefix='/api/patients')
    app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
    app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
