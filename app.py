import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_cors import CORS
from extensions import db, socketio

app = Flask(__name__)

socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")
CORS(app, supports_credentials=True)

# Blueprint imports and registration here

@app.route('/')
def test_socket():
    return render_template('main.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, host="0.0.0.0")

