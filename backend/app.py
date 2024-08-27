from flask import Flask
from config import DevelopmentConfig  # or ProductionConfig, TestingConfig based on your environment

# Import the Blueprints from the routes
from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp

app = Flask(__name__)
from flask_cors import CORS
app.config.from_object(DevelopmentConfig)

# Register the Blueprints with the Flask app
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
app.register_blueprint(staff_bp, url_prefix='/api/staff')

@app.route('/')
def index():
    return "Welcome to the EHPAD management API!"

if __name__ == '__main__':
    app.run()

