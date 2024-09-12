from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from extensions import db
from sqlalchemy import text

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://ehpad-admin:Memoire2024!@ehpadserver.database.windows.net:1433/ehpad?driver=ODBC+Driver+18+for+SQL+Server'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

# Import the Blueprints from the routes
from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp
from routes.azure_blob import azure_bp

# Register the Blueprints with the Flask app
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
app.register_blueprint(azure_bp, url_prefix='/api/azure')
app.register_blueprint(staff_bp, url_prefix='/api/staff')


@app.route('/')
def home():
    html = """
    <html>
        <head>
            <title>Human Falling Detection API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                a { text-decoration: none; color: #007BFF; }
                ul { list-style-type: none; padding: 0; }
                li { margin: 10px 0; }
                .container { width: 80%; margin: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Bienvenue sur l'interface de l'API</h1>
                <p>Cliquez sur les liens ci-dessous pour accéder aux différentes routes de l'API :</p>
                <ul>
                    <li><a href="/api/rooms">Gestion des chambres (Rooms)</a></li>
                    <li><a href="/api/incidents">Gestion des incidents (Incidents)</a></li>
                    <li><a href="/api/azure">Stockage Azure (Azure Blob)</a></li>
                    <li><a href="/api/staff">Gestion du personnel (Staff)</a></li>
                    <li><a href="/test_db">Tester la connexion à la base de données</a></li>
                </ul>
            </div>
        </body>
    </html>
    """
    return render_template_string(html)

@app.route('/test_db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return "Database connection is working!", 200
    except Exception as e:
        return f"Error connecting to the database: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)