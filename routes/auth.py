from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import Ehpad  # Utiliser le modèle EHPAD que nous avons créé
import jwt
import datetime

auth_bp = Blueprint('auth_bp', __name__)

SECRET_KEY = "testcle"  # À changer par une vraie clé secrète

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('password_hash'):
        return jsonify({"message": "Nom d'utilisateur et mot de passe requis"}), 400

    # Chercher l'EHPAD par nom d'utilisateur
    ehpad = Ehpad.query.filter_by(name=data['name']).first()

    if not ehpad:
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