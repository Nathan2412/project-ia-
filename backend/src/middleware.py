"""
Middleware d'authentification pour l'API Flask.
Gère la vérification des tokens et l'autorisation d'accès.
"""

from flask import request, jsonify, g
from functools import wraps
from src.auth import verify_jwt_token

def init_auth_middleware(app):
    """
    Initialise le middleware d'authentification pour l'application Flask.
    
    Args:
        app: Instance Flask
    """
    
    @app.before_request
    def before_request():
        """
        Exécuté avant chaque requête pour gérer l'authentification.
        """
        # Routes publiques qui ne nécessitent pas d'authentification
        public_routes = [
            '/api/login',
            '/api/register',
            '/api/genres',
            '/api/services',
            '/api/ping'
        ]
        
        # Vérifier si la route est publique
        if request.endpoint and any(request.path.startswith(route) for route in public_routes):
            return
        
        # Pour les autres routes, vérifier l'authentification
        if request.path.startswith('/api/'):
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
            
            # Stocker les informations utilisateur dans g
            g.current_user = {
                'user_id': payload['user_id'],
                'username': payload['username']
            }

def check_user_access(user_id: int) -> bool:
    """
    Vérifie si l'utilisateur connecté peut accéder aux données de l'utilisateur spécifié.
    
    Args:
        user_id: ID de l'utilisateur à vérifier
    
    Returns:
        bool: True si l'accès est autorisé
    """
    if not hasattr(g, 'current_user'):
        return False
    
    return g.current_user['user_id'] == user_id

def get_current_user():
    """
    Retourne l'utilisateur actuellement connecté.
    
    Returns:
        dict: Informations de l'utilisateur connecté ou None
    """
    return getattr(g, 'current_user', None)

class AuthError(Exception):
    """
    Exception personnalisée pour les erreurs d'authentification.
    """
    def __init__(self, message, status_code=401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def require_auth_for_user(user_id: int):
    """
    Vérifie que l'utilisateur connecté peut accéder aux données de l'utilisateur spécifié.
    
    Args:
        user_id: ID de l'utilisateur
    
    Raises:
        AuthError: Si l'accès n'est pas autorisé
    """
    current_user = get_current_user()
    
    if not current_user:
        raise AuthError("Authentification requise", 401)
    
    if current_user['user_id'] != user_id:
        raise AuthError("Accès non autorisé à ce compte", 403)

def handle_auth_error(error):
    """
    Gestionnaire d'erreur pour les exceptions d'authentification.
    
    Args:
        error: Instance d'AuthError
    
    Returns:
        Response: Réponse JSON avec l'erreur
    """
    return jsonify({'error': error.message}), error.status_code
