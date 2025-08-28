"""
Routes d'authentification pour l'API Flask.
Gère les endpoints de connexion, déconnexion et inscription.
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth import authenticate_user, create_user_with_password, generate_jwt_token, hash_password, verify_password
from models import db, User
from src.middleware import get_current_user, require_auth_for_user

# Créer un blueprint pour les routes d'authentification
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """
    Endpoint de connexion utilisateur.
    
    Body JSON attendu:
    {
        "email": "user@example.com",
        "password": "mot_de_passe"
    }
    
    Returns:
        JSON: Token d'authentification et informations utilisateur
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        # Authentifier l'utilisateur
        user = authenticate_user(email, password)
        
        if user is None:
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Générer un token JWT
        token = generate_jwt_token(user['id'], user['name'])
        
        return jsonify({
            'message': 'Connexion réussie',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user.get('email', ''),
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
        "name": "nom_utilisateur",
        "email": "user@example.com",
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
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not name or not email or not password:
            return jsonify({'error': 'Nom, email et mot de passe requis'}), 400
        
        # Validation de l'email
        if '@' not in email:
            return jsonify({'error': 'Adresse email invalide'}), 400
        
        # Validation du mot de passe
        if len(password) < 6:
            return jsonify({'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        
        # Validation du nom d'utilisateur
        if len(name) < 3:
            return jsonify({'error': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'}), 400
        
        # Récupérer les préférences (optionnelles)
        preferences = data.get('preferences', {})
        
        try:
            # Vérifier si l'email existe déjà
            existing_user = User.find_by_email(email)
            if existing_user:
                return jsonify({'error': 'Un compte avec cet email existe déjà'}), 400
            
            # Créer l'utilisateur avec email et mot de passe
            new_user = create_user_with_password(
                name=name,
                email=email,
                password=password,
                genres_likes=preferences.get('genres_likes', []),
                genres_dislikes=preferences.get('genres_dislikes', []),
                directors_likes=preferences.get('directors_likes', []),
                keywords_likes=preferences.get('keywords_likes', []),
                mood_preferences=preferences.get('mood_preferences', []),
                rating_min=preferences.get('rating_min', 7.0),
                streaming_services=preferences.get('streaming_services', [])
            )
            
            # Créer un objet User SQLAlchemy
            user = User(
                name=new_user['name'],
                email=new_user['email'],
                password_hash=new_user['auth']['password_hash'],
                password_salt=new_user['auth']['salt'],
                preferences=new_user['preferences']
            )
            
            # Ajouter l'utilisateur à la base de données
            db.session.add(user)
            db.session.commit()
            
            # TODO: Ajouter le service d'email plus tard
            # try:
            #     email_sent = email_service.send_welcome_email(user.email, user.name)
            #     if email_sent:
            #         print(f"✅ Email de bienvenue envoyé à {user.email}")
            #     else:
            #         print(f"⚠️  Email de bienvenue non envoyé à {user.email}")
            # except Exception as email_error:
            #     print(f"❌ Erreur lors de l'envoi de l'email de bienvenue: {str(email_error)}")
            #     # Ne pas faire échouer l'inscription si l'email ne peut pas être envoyé
            
            # Générer un token JWT
            token = generate_jwt_token(user.id, user.name)
            
            # Retourner la réponse sans les informations d'authentification
            user_response = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'preferences': user.preferences
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
    
    # Récupérer les informations complètes de l'utilisateur depuis la base de données
    user = User.query.get(current_user['user_id'])
    if user:
        user_info = {
            'id': user.id,
            'name': user.name,
            'preferences': user.preferences or {}
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
        
        # Récupérer l'utilisateur depuis la base de données
        user = User.query.get(current_user['user_id'])
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Vérifier l'ancien mot de passe
        if not verify_password(current_password, user.password_hash, user.password_salt):
            return jsonify({'error': 'Mot de passe actuel incorrect'}), 401
        
        # Hash du nouveau mot de passe
        new_password_hash, new_salt = hash_password(new_password)
        
        # Mettre à jour le mot de passe
        user.password_hash = new_password_hash
        user.password_salt = new_salt
        
        # Sauvegarder les changements
        try:
            db.session.commit()
            return jsonify({'message': 'Mot de passe modifié avec succès'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Erreur lors de la mise à jour'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du changement de mot de passe: {str(e)}'}), 500
