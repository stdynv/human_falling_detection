from flask import Flask, render_template_string
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# from extensions import db
# from sqlalchemy import text

app = Flask(__name__)



# Import the Blueprints from the routes
# from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp
from routes.azure_blob import azure_bp

# Register the Blueprints with the Flask app
# app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
app.register_blueprint(azure_bp, url_prefix='/api/azure')
app.register_blueprint(staff_bp, url_prefix='/api/staff')

@app.route('/')
def index():
    return "Welcome to the EHPAD management API!"


if __name__ == '__main__':
    app.run(debug=True,port=8000,host="0.0.0.0")
