
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from extensions import db, socketio  # Import socketio from extensions

app = Flask(__name__)

# Initialize extensions
db.init_app(app)
socketio.init_app(app, cors_allowed_origins=["https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net",'*'])
CORS(app, supports_credentials=True)

# Import the Blueprints from the routes
from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp
# from routes.azure_blob import azure_bp

# Register the Blueprints with the Flask app
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')

@app.route('/')
def home():
    return render_template('main.html')

# Run the app using SocketIO instead of app.run
if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, host="0.0.0.0")
