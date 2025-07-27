"""
Routes d'authentification pour l'API Flask.
Gère les endpoints de connexion, déconnexion et inscription.
"""

from flask import Blueprint, request, jsonify
from src.auth import authenticate_user, create_user_with_password, generate_jwt_token
from data.user_database import add_user, load_users

# Créer un blueprint pour les routes d'authentification
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """
    Endpoint de connexion utilisateur.
    
    Body JSON attendu:
    {
        "username": "nom_utilisateur",
        "password": "mot_de_passe"
    }
    
    Returns:
        JSON: Token d'authentification et informations utilisateur
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
        
        # Authentifier l'utilisateur
        user = authenticate_user(username, password)
        
        if user is None:
            return jsonify({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401
        
        # Générer un token JWT
        token = generate_jwt_token(user['id'], user['name'])
        
        return jsonify({
            'message': 'Connexion réussie',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'preferences': user['preferences']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la connexion: {str(e)}'}), 500

@auth_bp.route('/api/register', methods=['POST'])
def register():
    """
    Endpoint d'inscription utilisateur.
    
    Body JSON attendu:
    {
        "username": "nom_utilisateur",
        "password": "mot_de_passe",
        "preferences": {
            "genres_likes": [...],
            "genres_dislikes": [...],
            // autres préférences optionnelles
        }
    }
    
    Returns:
        JSON: Confirmation d'inscription et token d'authentification
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
        
        # Validation du mot de passe
        if len(password) < 6:
            return jsonify({'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        
        # Validation du nom d'utilisateur
        if len(username) < 3:
            return jsonify({'error': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'}), 400
        
        # Récupérer les préférences (optionnelles)
        preferences = data.get('preferences', {})
        
        try:
            # Créer l'utilisateur avec mot de passe
            new_user = create_user_with_password(
                name=username,
                password=password,
                genres_likes=preferences.get('genres_likes', []),
                genres_dislikes=preferences.get('genres_dislikes', []),
                directors_likes=preferences.get('directors_likes', []),
                keywords_likes=preferences.get('keywords_likes', []),
                mood_preferences=preferences.get('mood_preferences', []),
                rating_min=preferences.get('rating_min', 7.0),
                streaming_services=preferences.get('streaming_services', [])
            )
            
            # Ajouter l'utilisateur à la base de données
            created_user = add_user(new_user)
            
            # Générer un token JWT
            token = generate_jwt_token(created_user['id'], created_user['name'])
            
            # Retourner la réponse sans les informations d'authentification
            user_response = {
                'id': created_user['id'],
                'name': created_user['name'],
                'preferences': created_user['preferences']
            }
            
            return jsonify({
                'message': 'Inscription réussie',
                'token': token,
                'user': user_response
            }), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 409  # Conflict
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'inscription: {str(e)}'}), 500

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """
    Endpoint de déconnexion utilisateur.
    Note: Avec JWT, la déconnexion côté serveur est optionnelle
    car les tokens ont une durée de vie limitée.
    """
    return jsonify({'message': 'Déconnexion réussie'}), 200

@auth_bp.route('/api/verify-token', methods=['GET'])
def verify_token():
    """
    Endpoint pour vérifier la validité d'un token.
    Nécessite un token d'authentification valide.
    """
    from src.middleware import get_current_user
    
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Token invalide'}), 401
    
    # Récupérer les informations complètes de l'utilisateur
    users = load_users()
    for user in users:
        if user['id'] == current_user['user_id']:
            user_info = {
                'id': user['id'],
                'name': user['name'],
                'preferences': user['preferences']
            }
            return jsonify({
                'message': 'Token valide',
                'user': user_info
            }), 200
    
    return jsonify({'error': 'Utilisateur non trouvé'}), 404

@auth_bp.route('/api/change-password', methods=['POST'])
def change_password():
    """
    Endpoint pour changer le mot de passe d'un utilisateur.
    Nécessite un token d'authentification valide.
    
    Body JSON attendu:
    {
        "current_password": "ancien_mot_de_passe",
        "new_password": "nouveau_mot_de_passe"
    }
    """
    from src.middleware import get_current_user
    from src.auth import verify_password, hash_password
    from data.user_database import update_user
    
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentification requise'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Mot de passe actuel et nouveau mot de passe requis'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Le nouveau mot de passe doit contenir au moins 6 caractères'}), 400
        
        # Récupérer l'utilisateur complet
        users = load_users()
        user_to_update = None
        for user in users:
            if user['id'] == current_user['user_id']:
                user_to_update = user
                break
        
        if not user_to_update or 'auth' not in user_to_update:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Vérifier l'ancien mot de passe
        stored_hash = user_to_update['auth']['password_hash']
        salt = user_to_update['auth']['salt']
        
        if not verify_password(current_password, stored_hash, salt):
            return jsonify({'error': 'Mot de passe actuel incorrect'}), 401
        
        # Hash du nouveau mot de passe
        new_password_hash, new_salt = hash_password(new_password)
        
        # Mettre à jour le mot de passe
        user_to_update['auth']['password_hash'] = new_password_hash
        user_to_update['auth']['salt'] = new_salt
        
        # Sauvegarder les changements
        if update_user(user_to_update):
            return jsonify({'message': 'Mot de passe modifié avec succès'}), 200
        else:
            return jsonify({'error': 'Erreur lors de la mise à jour'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du changement de mot de passe: {str(e)}'}), 500
