from eventlet import monkey_patch
monkey_patch() 

from flask import Flask, render_template
from flask_cors import CORS
from extensions import db, socketio 




app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://ehpad-admin:Memoire2024!@ehpadserver.database.windows.net:1433/ehpad?driver=ODBC+Driver+18+for+SQL+Server'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
socketio(app, cors_allowed_origins="https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net")
CORS(app)


# Blueprint imports and registration here
# Import the Blueprints from the routes
from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp
# from routes.azure_blob import azure_bp

# Register the Blueprints with the Flask app
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')

@app.route('/')
def test_socket():
    return render_template('main.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000, host="0.0.0.0")
