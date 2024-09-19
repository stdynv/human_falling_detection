from flask import Flask, render_template
from flask_cors import CORS
import socket
from extensions import db, socketio
import logging
from config import Config  # Ensure this path is correct as per your project structure
import os

# Configure logging
logging.basicConfig(level=logging.INFO)


app = Flask(__name__)


app.config.from_object(
    Config
)

# Initialize the SQLAlchemy extension with the Flask app
db.init_app(app) 

socketio.init_app(
    app,
    cors_allowed_origins="*",
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
)
CORS(app)  # Enable CORS

# Blueprint imports and registration
from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp
from routes.auth import auth_bp , token_required


# Register the Blueprints with the Flask app
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/')
def login_page():
    return render_template('auth-login-basic.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('auth-forgot-password-basic.html')

@app.route('/chambres')
def chambres_page():
    return render_template('chambres.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/tables-basic')
def tables_page():
    return render_template('tables-basic.html')

# Test route to check WebSocket connection
@app.route("/dashboard")
def test_socket():
    server_url = os.getenv("SERVER")
    hostname = socket.gethostname()
    return render_template("main.html", socket_url=hostname)


# Run the app using eventlet
if __name__ == "__main__":
    # Ensure eventlet works properly with other libraries
    socketio.run(app, debug=True, host="0.0.0.0")
