from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from extensions import db, socketio  # Import socketio from extensions
from flask_socketio import SocketIO

# Initialize the Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://ehpad-admin:Memoire2024!@ehpadserver.database.windows.net:1433/ehpad?driver=ODBC+Driver+18+for+SQL+Server'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Initialize SocketIO with eventlet async mode
socketio = SocketIO(app, debug=True, cors_allowed_origins="*")

# CORS configuration to allow your Azure URL
CORS(app, resources={r"/*": {"origins": "https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net"}})

# Import the Blueprints from the routes
from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp

# Register the Blueprints with the Flask app
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')

@app.route('/')
def test_socket():
    return render_template('main.html')

# Run the app using SocketIO with eventlet
if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, host="0.0.0.0")
