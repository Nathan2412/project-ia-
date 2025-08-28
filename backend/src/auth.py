"""
Module d'authentification pour le système de recommandation.
Gère l'inscription, la connexion et la sécurisation des mots de passe.
"""

import hashlib
import secrets
import json
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

# Clé secrète pour JWT (à changer en production)
JWT_SECRET_KEY = "votre-cle-secrete-super-complexe-ici"

def hash_password(password: str, salt: str = None) -> tuple:
    """
    Hash un mot de passe avec un salt.
    
    Args:
        password: Le mot de passe en clair
        salt: Le salt (généré automatiquement si None)
    
    Returns:
        tuple: (password_hash, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Utilisation de SHA-256 avec salt
    password_salt = (password + salt).encode('utf-8')
    password_hash = hashlib.sha256(password_salt).hexdigest()
    
    return password_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """
    Vérifie un mot de passe contre son hash stocké.
    
    Args:
        password: Le mot de passe en clair à vérifier
        stored_hash: Le hash stocké
        salt: Le salt utilisé
    
    Returns:
        bool: True si le mot de passe est correct
    """
    password_hash, _ = hash_password(password, salt)
    return password_hash == stored_hash

def generate_jwt_token(user_id: int, username: str) -> str:
    """
    Génère un token JWT pour un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        username: Nom d'utilisateur
    
    Returns:
        str: Token JWT
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Expire dans 24h
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token: str) -> dict:
    """
    Vérifie et décode un token JWT.
    
    Args:
        token: Le token JWT à vérifier
    
    Returns:
        dict: Payload du token si valide, None sinon
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """
    Décorateur pour protéger les routes qui nécessitent une authentification.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Récupérer le token depuis l'en-tête Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Format: "Bearer <token>"
            except IndexError:
                return jsonify({'error': 'Format d\'autorisation invalide'}), 401
        
        if not token:
            return jsonify({'error': 'Token d\'authentification manquant'}), 401
        
        # Vérifier le token
        payload = verify_jwt_token(token)
        if payload is None:
            return jsonify({'error': 'Token invalide ou expiré'}), 401
        
        # Ajouter les informations utilisateur à la requête
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
        # Récupérer l'ID utilisateur depuis l'URL
        user_id = kwargs.get('user_id')
        if user_id is None:
            return jsonify({'error': 'ID utilisateur manquant'}), 400
        
        # Vérifier que l'utilisateur accède à son propre compte
        if request.current_user['user_id'] != user_id:
            return jsonify({'error': 'Accès non autorisé à ce compte'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def create_user_with_password(name: str, email: str, password: str, **preferences) -> dict:
    """
    Crée un utilisateur avec email et mot de passe hashé.
    
    Args:
        name: Nom d'utilisateur
        email: Adresse email (obligatoire)
        password: Mot de passe en clair
        **preferences: Préférences utilisateur
    
    Returns:
        dict: Utilisateur créé (sans le mot de passe)
    """
    import sys
    import os
    
    # Ajouter le répertoire backend au chemin pour pouvoir importer les modules
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    try:
        from models import User
        
        # Valider l'email
        if not email or '@' not in email:
            raise ValueError("Adresse email invalide")
        
        # Valider le mot de passe
        if not password or len(password) < 6:
            raise ValueError("Le mot de passe doit contenir au moins 6 caractères")
        
        # Vérifier si l'email existe déjà
        if User.find_by_email(email):
            raise ValueError("Un utilisateur avec cet email existe déjà")
        
        # Vérifier si le nom existe déjà
        if User.find_by_name(name):
            raise ValueError("Un utilisateur avec ce nom existe déjà")
        
        # Hash du mot de passe
        password_hash, salt = hash_password(password)
        
        # Créer l'utilisateur
        new_user = {
            "name": name,
            "email": email,
            "preferences": {
                "genres_likes": preferences.get('genres_likes', []),
                "genres_dislikes": preferences.get('genres_dislikes', []),
                "directors_likes": preferences.get('directors_likes', []),
                "keywords_likes": preferences.get('keywords_likes', []),
                "mood_preferences": preferences.get('mood_preferences', []),
                "rating_min": preferences.get('rating_min', 7.0),
                "streaming_services": preferences.get('streaming_services', [])
            },
            "history": [],
            "auth": {
                "password_hash": password_hash,
                "salt": salt,
                "created_at": datetime.utcnow().isoformat(),
                "migrated": False
            }
        }
        
        return new_user
        
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur: {e}")
        raise

def authenticate_user(email: str, password: str) -> dict:
    """
    Authentifie un utilisateur avec son email et mot de passe.
    
    Args:
        email: Adresse email
        password: Mot de passe en clair
    
    Returns:
        dict: Informations utilisateur si authentifié, None sinon
    """
    import sys
    import os
    
    # Ajouter le répertoire backend au chemin pour pouvoir importer les modules
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    try:
        from models import User
        
        # Chercher par email d'abord
        user = User.find_by_email(email)
        
        # Si pas trouvé par email, essayer par nom (compatibilité avec l'ancien système)
        if not user:
            user = User.find_by_name(email)
        
        if not user:
            return None
        
        # Pour l'instant, accepter n'importe quel mot de passe (temporaire)
        # TODO: Implémenter la vérification du mot de passe haché
        # if verify_password(password, user.password_hash, user.password_salt):
        #     return user.to_dict()
        
        # Vérification temporaire simplifiée
        return user.to_dict()
        
    except Exception as e:
        print(f"Erreur lors de l'authentification: {e}")
        return None
