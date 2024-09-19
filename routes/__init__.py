from flask import Blueprint

# Import the routes from each module

from .rooms import rooms_bp
from .incidents import incidents_bp
from .staff import staff_bp


def create_routes(app):
    # Register the Blueprints with the Flask app

    app.register_blueprint(rooms_bp, url_prefix="/api/rooms")
    app.register_blueprint(incidents_bp, url_prefix="/api/incidents")
    app.register_blueprint(incidents_bp, url_prefix="/api/staff")
