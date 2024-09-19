from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import Ehpad  # Utiliser le modèle EHPAD que nous avons créé
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth_bp', __name__)

SECRET_KEY = "testcle"  # À changer par une vraie clé secrète

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('password_hash'):
        return jsonify({"message": "Nom d'utilisateur et mot de passe requis"}), 400

    # Chercher l'EHPAD par nom d'utilisateur
    ehpad = Ehpad.query.filter_by(name=data['name']).first()

    if not ehpad or not check_password_hash(ehpad.password_hash, data['password_hash']):
        return jsonify({"message": "Informations d'identification non correctes"}), 401

    # Générer un token JWT
    token = jwt.encode({
        'ehpad_id': ehpad.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)  # Expire dans 12h
    }, SECRET_KEY)

    return jsonify({"token": token}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Du côté serveur, nous ne gérons pas les sessions, donc nous pouvons simplement informer le client
    return jsonify({"message": "Déconnexion réussie, veuillez supprimer le token du stockage local."}), 200

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Bearer <token>

        if not token:
            return jsonify({'message': 'Token manquant!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_ehpad = Ehpad.query.filter_by(id=data['ehpad_id']).first()
        except:
            return jsonify({'message': 'Token invalide!'}), 401

        return f(current_ehpad, *args, **kwargs)

    return decorated