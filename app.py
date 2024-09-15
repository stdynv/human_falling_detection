import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from extensions import db, socketio

app = Flask(__name__)

# Initialize extensions
db.init_app(app)
socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")
CORS(app, supports_credentials=True)

# Import the Blueprints from the routes
from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp

# Register the Blueprints with the Flask app
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')

@app.route('/')
def home():
    return render_template('main.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=8000)
