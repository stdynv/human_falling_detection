import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_cors import CORS
from extensions import db, socketio

app = Flask(__name__)

socketio.init_app(app, cors_allowed_origins=["https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net"])
CORS(app, resources={r"/*": {"origins": "https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net"}})


# Blueprint imports and registration here

@app.route('/')
def test_socket():
    return render_template('main.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, host="0.0.0.0")

