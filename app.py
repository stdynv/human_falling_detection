from eventlet import monkey_patch
monkey_patch()  # Monkey patching for eventlet must happen at the very top

from flask import Flask, render_template
from flask_cors import CORS
from extensions import db, socketio

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://ehpad-admin:Memoire2024!@ehpadserver.database.windows.net:1433/ehpad?driver=ODBC+Driver+18+for+SQL+Server'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)  # Initialize the SQLAlchemy extension with the Flask app
socketio.init_app(app, cors_allowed_origins="*")  # Properly initialize SocketIO
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

# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, host="0.0.0.0")
