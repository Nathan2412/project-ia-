"""
Module d'authentification pour le système de recommandation.
Gère l'inscription, la connexion et la sécurisation des mots de passe.
"""

import hashlib
import hmac
import os
import secrets
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

# Clé secrète pour JWT - chargée depuis l'environnement (obligatoire en production)
JWT_SECRET_KEY = os.environ.get(
    'JWT_SECRET_KEY',
    'dev-only-change-me-in-production-4f8a9c2e1b6d7e5a3f2c9b8d4e6a1c7b'
)

if JWT_SECRET_KEY.startswith('dev-only') and os.environ.get('FLASK_ENV') == 'production':
    raise RuntimeError(
        "JWT_SECRET_KEY doit être défini via variable d'environnement en production"
    )


def hash_password(password: str, salt: str = None) -> tuple:
    """
    Hash un mot de passe avec un salt (SHA-256 legacy).
    Conservé pour compatibilité avec les anciens comptes.
    Les nouveaux comptes utilisent werkzeug.generate_password_hash.
    """
    if salt is None:
        salt = secrets.token_hex(32)

    password_salt = (password + salt).encode('utf-8')
    password_hash = hashlib.sha256(password_salt).hexdigest()

    return password_hash, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """
    Vérifie un mot de passe contre son hash stocké.
    Supporte les hashes werkzeug (préférés) et les hashes SHA-256 legacy.
    """
    if not password or not stored_hash:
        return False

    # Format werkzeug (pbkdf2/scrypt) - préféré
    if stored_hash.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
        try:
            return check_password_hash(stored_hash, password)
        except Exception:
            return False

    # Fallback legacy SHA-256 + salt
    if not salt:
        return False
    computed_hash, _ = hash_password(password, salt)
    # Comparaison temporellement constante pour éviter les attaques timing
    return hmac.compare_digest(computed_hash, stored_hash)


def generate_jwt_token(user_id: int, username: str) -> str:
    """Génère un token JWT pour un utilisateur (expire dans 24h)."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    # PyJWT 2.x renvoie str, mais PyJWT 1.x renvoyait bytes — normaliser
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def verify_jwt_token(token: str) -> dict:
    """Vérifie et décode un token JWT. Retourne None si invalide."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Décorateur pour protéger les routes qui nécessitent une authentification."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
            else:
                return jsonify({'error': "Format d'autorisation invalide"}), 401

        if not token:
            return jsonify({'error': "Token d'authentification manquant"}), 401

        payload = verify_jwt_token(token)
        if payload is None:
            return jsonify({'error': 'Token invalide ou expiré'}), 401

        request.current_user = {
            'user_id': payload['user_id'],
            'username': payload['username']
        }

        return f(*args, **kwargs)

    return decorated_function


def require_own_account(f):
    """
    Décorateur pour s'assurer qu'un utilisateur ne peut accéder qu'à son propre compte.
    À utiliser après require_auth.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            return jsonify({'error': 'ID utilisateur manquant'}), 400

        current_user = getattr(request, 'current_user', None)
        if not current_user or current_user['user_id'] != user_id:
            return jsonify({'error': 'Accès non autorisé à ce compte'}), 403

        return f(*args, **kwargs)

    return decorated_function


def create_user_with_password(name: str, email: str, password: str, **preferences) -> dict:
    """
    Prépare les données pour créer un utilisateur avec email et mot de passe hashé.
    Retourne un dictionnaire prêt à être persisté (ne touche pas à la DB).
    """
    from models import User

    if not email or '@' not in email:
        raise ValueError("Adresse email invalide")

    if not password or len(password) < 6:
        raise ValueError("Le mot de passe doit contenir au moins 6 caractères")

    if User.find_by_email(email):
        raise ValueError("Un utilisateur avec cet email existe déjà")

    if User.find_by_name(name):
        raise ValueError("Un utilisateur avec ce nom existe déjà")

    # Utiliser werkzeug (pbkdf2) — plus sûr que SHA-256 simple
    password_hash = generate_password_hash(password)

    return {
        "name": name,
        "email": email,
        "preferences": {
            "genres_likes": preferences.get('genres_likes', []),
            "genres_dislikes": preferences.get('genres_dislikes', []),
            "directors_likes": preferences.get('directors_likes', []),
            "keywords_likes": preferences.get('keywords_likes', []),
            "mood_preferences": preferences.get('mood_preferences', []),
            "rating_min": preferences.get('rating_min', 7.0),
            "streaming_services": preferences.get('streaming_services', []),
            "watch_history": []
        },
        "auth": {
            "password_hash": password_hash,
            "salt": "",  # werkzeug intègre le salt dans le hash
            "created_at": datetime.utcnow().isoformat()
        }
    }


def authenticate_user(email: str, password: str) -> dict:
    """
    Authentifie un utilisateur avec son email et mot de passe.
    Retourne le dict utilisateur si succès, None sinon.
    """
    from models import User

    if not email or not password:
        return None

    user = User.query.filter_by(email=email).first()
    if not user:
        return None

    if not verify_password(password, user.password_hash, user.password_salt or ""):
        return None

    return user.to_dict()
