from flask import Flask, render_template
from flask_cors import CORS
from extensions import db, socketio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://ehpad-admin:Memoire2024!@ehpadserver.database.windows.net:1433/ehpad?driver=ODBC+Driver+18+for+SQL+Server'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)  # Initialize the SQLAlchemy extension with the Flask app
socketio.init_app(app, cors_allowed_origins="*", engineio_logger=True, ping_timeout=60, ping_interval=25)
CORS(app)  # Enable CORS

# Blueprint imports and registration
from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp

# Register the Blueprints with the Flask app
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')

# Test route to check WebSocket connection
@app.route('/')
def test_socket():
    return render_template('main.html')

# Run the app using eventlet
if __name__ == '__main__':
    # Ensure eventlet works properly with other libraries
    socketio.run(app, debug=True, host="0.0.0.0", port=8000)
