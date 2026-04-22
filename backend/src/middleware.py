"""
Middleware d'authentification pour l'API Flask.
Gère la vérification des tokens et l'autorisation d'accès.
"""

from flask import request, jsonify, g
from src.auth import verify_jwt_token

# Routes qui ne nécessitent AUCUNE authentification (match exact)
EXACT_PUBLIC_ROUTES = {
    '/api/ping',
    '/api/login',
    '/api/register',
    '/api/genres',
    '/api/services',
    '/api/logout',
}


def _is_public_route(path: str) -> bool:
    """Détermine si une route est publique (ne nécessite pas d'authentification)."""
    if path in EXACT_PUBLIC_ROUTES:
        return True
    # Les routes servant le frontend (non-/api/) sont publiques par défaut
    if not path.startswith('/api/'):
        return True
    return False


def init_auth_middleware(app):
    """Initialise le middleware d'authentification pour l'application Flask."""

    @app.before_request
    def before_request():
        # Laisser passer les requêtes CORS preflight sans authentification
        if request.method == 'OPTIONS':
            return

        if _is_public_route(request.path):
            return

        # Pour les autres routes /api/*, vérifier l'authentification
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
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

        g.current_user = {
            'user_id': payload['user_id'],
            'username': payload['username']
        }


def check_user_access(user_id: int) -> bool:
    """Vérifie si l'utilisateur connecté peut accéder aux données de l'utilisateur spécifié."""
    current = getattr(g, 'current_user', None)
    if not current:
        return False
    return current['user_id'] == user_id


def get_current_user():
    """Retourne l'utilisateur actuellement connecté ou None."""
    return getattr(g, 'current_user', None)


class AuthError(Exception):
    """Exception personnalisée pour les erreurs d'authentification."""

    def __init__(self, message, status_code=401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def require_auth_for_user(user_id: int):
    """Lève une AuthError si l'utilisateur connecté ne peut pas accéder au compte cible."""
    current_user = get_current_user()
    if not current_user:
        raise AuthError("Authentification requise", 401)
    if current_user['user_id'] != user_id:
        raise AuthError("Accès non autorisé à ce compte", 403)


def handle_auth_error(error):
    """Gestionnaire d'erreur pour les exceptions d'authentification."""
    return jsonify({'error': error.message}), error.status_code
