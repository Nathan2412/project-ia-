"""
API REST pour le système de recommandation de films et séries.
Ce fichier permet d'exposer les fonctionnalités du système via une API HTTP.
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
import sys
from werkzeug.security import generate_password_hash
import json

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.recommendation_engine_v2 import modular_engine
from models import db, User
from src.middleware import init_auth_middleware, check_user_access, get_current_user, AuthError, handle_auth_error

app = Flask(__name__)
CORS(app)  # Activer CORS pour permettre les requêtes depuis le frontend

# Configuration SQLAlchemy pour MariaDB (local et serveur)
import os
DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:motdepasse123@127.0.0.1:3306/whattowatch')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialisation de la base
db.init_app(app)

# Initialiser le middleware d'authentification
init_auth_middleware(app)

# Note: Les routes d'authentification sont gérées directement dans ce fichier
# pour éviter les conflits de routes

# Gestionnaire d'erreur pour l'authentification
app.register_error_handler(AuthError, handle_auth_error)

# Note: Les utilisateurs sont maintenant gérés par SQLAlchemy via la classe User

# Endpoint de test simple (sans authentification)
@app.route('/api/ping', methods=['GET'])
def ping():
    """Endpoint simple pour tester que l'API fonctionne."""
    return jsonify({
        'status': 'ok', 
        'message': 'WhatToWatch API is running',
        'version': '2.0'
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """DÉSACTIVÉ pour des raisons de sécurité."""
    return jsonify({'error': 'Endpoint désactivé. Utilisez /api/register pour créer un compte.'}), 403

@app.route('/api/login', methods=['POST'])
def login_user():
    """Connexion utilisateur avec email et mot de passe."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données JSON manquantes'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
            
        # Rechercher l'utilisateur par email
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
            
        # Vérifier le mot de passe avec Werkzeug (compatible avec notre système d'inscription)
        from werkzeug.security import check_password_hash
        if not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Générer un token JWT pour cet utilisateur
        from src.auth import generate_jwt_token
        token = generate_jwt_token(user.id, user.name)
        
        # Retourner les données utilisateur avec le token
        response_data = {
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email or '',
                'preferences': user.preferences or {}
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la connexion: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retourne un utilisateur spécifique - NÉCESSITE UNE AUTHENTIFICATION."""
    try:
        # Vérifier l'authentification
        if not check_user_access(user_id):
            return jsonify({'error': 'Accès non autorisé à ce compte'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Utilisateur authentifié - retourner les détails complets
        sanitized_user = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'preferences': user.preferences or {},
            'watch_history': user.preferences.get('watch_history', []) if user.preferences else []
        }
        return jsonify(sanitized_user)
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération de l\'utilisateur: {str(e)}'}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Crée un nouvel utilisateur."""
    try:
        data = request.get_json()
        
        # Extraire les données
        name = data.get('name')
        email = data.get('email', f"{name}@example.com")  # Email par défaut si non fourni
        preferences = data
        
        if not name:
            return jsonify({'error': 'Le nom est requis'}), 400
        
        # Vérifier si l'utilisateur existe déjà par nom
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            return jsonify({'error': 'Un utilisateur avec ce nom existe déjà'}), 409
        
        # Créer l'utilisateur sans mot de passe (système simplifié)
        new_user = User(
            name=name,
            email=email,
            password_hash="",  # Pas de mot de passe pour le moment
            password_salt="",  
            preferences=preferences
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Retourner l'utilisateur créé avec ses préférences
        user_data = {
            'id': new_user.id,
            'name': new_user.name,
            'email': new_user.email,
            'preferences': new_user.preferences or {}
        }
        
        return jsonify(user_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la création de l\'utilisateur: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user_preferences(user_id):
    """Met à jour les préférences d'un utilisateur."""
    try:
        # Vérifier que l'utilisateur connecté peut modifier ce profil
        if not check_user_access(user_id):
            return jsonify({'error': 'Accès non autorisé à ce compte'}), 403
        
        data = request.json
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Initialiser les préférences si elles n'existent pas
        if user.preferences is None:
            user.preferences = {}
        
        # Mettre à jour le nom si présent
        if 'name' in data:
            user.name = data['name']
        # Mettre à jour les préférences
        if 'genres_likes' in data:
            user.preferences['genres_likes'] = data['genres_likes']
        if 'genres_dislikes' in data:
            user.preferences['genres_dislikes'] = data['genres_dislikes']
        if 'directors_likes' in data:
            user.preferences['directors_likes'] = data['directors_likes']
        if 'keywords_likes' in data:
            user.preferences['keywords_likes'] = data['keywords_likes']
        if 'rating_min' in data:
            user.preferences['rating_min'] = data['rating_min']
        if 'streaming_services' in data:
            user.preferences['streaming_services'] = data['streaming_services']
        
        # Marquer les préférences comme modifiées pour SQLAlchemy
        user.preferences = user.preferences.copy()
        
        # Sauvegarder les modifications
        try:
            db.session.commit()
            # Retourner l'utilisateur sans les informations d'authentification
            sanitized_user = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'preferences': user.preferences
            }
            return jsonify(sanitized_user)
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Erreur lors de la sauvegarde: {str(e)}'}), 500
        
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

@app.route('/api/genres', methods=['GET'])
def get_genres():
    """Récupère la liste des genres disponibles."""
    try:
        # Liste de genres par défaut
        genres = ["Action", "Aventure", "Animation", "Comédie", "Crime", 
                 "Documentaire", "Drame", "Famille", "Fantaisie", "Histoire", 
                 "Horreur", "Musique", "Mystère", "Romance", "Science-Fiction", 
                 "Thriller", "Guerre", "Western"]
        return jsonify(genres)
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la récupération des genres: {str(e)}',
            # Fournir une liste de genres par défaut
            'genres': ["Action", "Aventure", "Animation", "Comédie", "Crime", 
                       "Documentaire", "Drame", "Famille", "Fantaisie", "Histoire", 
                       "Horreur", "Musique", "Mystère", "Romance", "Science-Fiction", 
                       "Téléfilm", "Thriller", "Guerre", "Western"]
        }), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    """Récupère la liste des services de streaming disponibles."""
    from data.movies_series_database import STREAMING_SERVICES
    return jsonify(STREAMING_SERVICES)

@app.route('/api/providers', methods=['GET'])
def get_api_providers():
    """Récupère l'état des fournisseurs d'API disponibles."""
    from src.api_providers.multi_api_manager import MultiAPIManager
    api_manager = MultiAPIManager()
    
    try:
        # Tester tous les fournisseurs
        provider_status = api_manager.test_all_providers()
        available_providers = api_manager.get_available_providers()
        
        return jsonify({
            'available_providers': available_providers,
            'provider_status': provider_status,
            'total_providers': len(api_manager.providers)
        })
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la vérification des fournisseurs: {str(e)}',
            'available_providers': [],
            'provider_status': {}
        }), 500

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """Récupère des recommandations pour un utilisateur."""
    try:
        # Vérifier que l'utilisateur connecté peut accéder à ces recommandations
        if not check_user_access(user_id):
            return jsonify({'error': 'Accès non autorisé à ce compte'}), 403
        
        content_type = request.args.get('content_type', 'all')
        n = int(request.args.get('n', '5'))
        
        # Gérer les services de streaming (format flexible)
        streaming_services = None
        streaming_service = request.args.get('streaming_service', None)
        streaming_services_param = request.args.get('streaming_services', None)
        
        if streaming_services_param:
            # Format moderne avec liste
            if isinstance(streaming_services_param, str):
                streaming_services = streaming_services_param.split(',') if ',' in streaming_services_param else [streaming_services_param]
            else:
                streaming_services = streaming_services_param
        elif streaming_service:
            # Format legacy avec service unique
            streaming_services = streaming_service.split(',') if ',' in streaming_service else [streaming_service]
        
        # Vérifier les paramètres
        if content_type not in ['all', 'movies', 'series']:
            content_type = 'all'
        if n < 1 or n > 20:  # Limiter le nombre de recommandations
            n = 5
            
        # Debug - Log des paramètres
        print(f"🔍 DEBUG API Recommendations:")
        print(f"  - user_id: {user_id}")
        print(f"  - content_type: {content_type}")
        print(f"  - n: {n}")
        print(f"  - streaming_services: {streaming_services}")
            
        recommendations = modular_engine.get_recommendations(
            user_id, 
            n=n, 
            content_type=content_type, 
            streaming_services=streaming_services
        )
        
        print(f"✅ Recommandations générées: {len(recommendations)}")
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération des recommandations: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>/history', methods=['POST'])
def add_to_user_history(user_id):
    """Ajoute un élément à l'historique d'un utilisateur (nouvelle route)."""
    try:
        # Vérifier que l'utilisateur connecté peut modifier cet historique
        if not check_user_access(user_id):
            return jsonify({'error': 'Accès non autorisé à ce compte'}), 403
        
        data = request.get_json()
        item = data.get('item', {})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Initialiser les préférences si elles n'existent pas
        if user.preferences is None:
            user.preferences = {}
        
        # Ajouter à l'historique
        if 'watch_history' not in user.preferences:
            user.preferences['watch_history'] = []
        
        # Éviter les doublons
        history = user.preferences['watch_history']
        if not any(h.get('id') == item.get('id') and h.get('content_type') == item.get('content_type') for h in history):
            user.preferences['watch_history'].append(item)
            # Marquer comme modifié pour SQLAlchemy
            user.preferences = user.preferences.copy()
            db.session.commit()
        
        return jsonify({'success': True, 'message': 'Ajouté à l\'historique'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'ajout à l\'historique: {str(e)}'}), 500

@app.route('/api/history/<int:user_id>/<item_id>', methods=['POST'])
def add_to_history(user_id, item_id):
    """Ajoute un élément à l'historique d'un utilisateur."""
    try:
        # Vérifier que l'utilisateur connecté peut modifier cet historique
        if not check_user_access(user_id):
            return jsonify({'error': 'Accès non autorisé à ce compte'}), 403
        
        if modular_engine.update_user_history(user_id, item_id):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Erreur lors de la mise à jour de l\'historique'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la mise à jour de l\'historique: {str(e)}'}), 500

@app.route('/api/search', methods=['GET'])
def search_content():
    """Recherche de contenu via les APIs multiples."""
    try:
        # Vérifier l'authentification
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentification requise'}), 401
        
        query = request.args.get('q', '').strip()
        content_type = request.args.get('type', 'all')
        max_results = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify({'error': 'Paramètre de recherche requis'}), 400
        
        if max_results < 1 or max_results > 50:
            max_results = 20
        
        results = modular_engine.search_content(
            query=query,
            content_type=content_type,
            max_results=max_results
        )
        
        return jsonify(results)
        
    except AuthError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la recherche: {str(e)}'}), 500

@app.route('/api/trending', methods=['GET'])
def get_trending_content():
    """Récupère le contenu tendance."""
    try:
        # Vérifier l'authentification
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentification requise'}), 401
        
        content_type = request.args.get('type', 'all')
        max_results = int(request.args.get('limit', 20))
        
        if max_results < 1 or max_results > 50:
            max_results = 20
        
        results = modular_engine.get_trending_content(
            content_type=content_type,
            max_results=max_results
        )
        
        return jsonify(results)
        
    except AuthError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération du contenu tendance: {str(e)}'}), 500

@app.route('/api/streaming-services', methods=['GET'])
def get_streaming_services():
    """Retourne la liste des services de streaming supportés."""
    try:
        # Vérifier l'authentification
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentification requise'}), 401
        
        services = modular_engine.get_supported_streaming_services()
        return jsonify({
            'supported_services': services,
            'total_services': len(services)
        })
        
    except AuthError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération des services: {str(e)}'}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Vide le cache du système (admin uniquement)."""
    try:
        # Vérifier l'authentification
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentification requise'}), 401
        
        # Pour simplicité, tous les utilisateurs peuvent vider le cache
        # Dans un vrai système, on vérifierait les permissions admin
        modular_engine.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Cache vidé avec succès'
        })
        
    except AuthError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': f'Erreur lors du vidage du cache: {str(e)}'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """Endpoint pour l'inscription des nouveaux utilisateurs."""
    try:
        data = request.get_json()

        name = data.get('username') or data.get('name')
        email = data.get('email')
        password = data.get('password')
        preferences = data.get('preferences', {})

        if not name or not email or not password:
            return jsonify({'error': 'Champs requis manquants'}), 400

        # Vérifie si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Utilisateur déjà inscrit'}), 409

        # Hash du mot de passe
        password_hash = generate_password_hash(password)

        # Créer l'utilisateur
        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            password_salt="",  # Ajouter un salt vide pour la compatibilité
            preferences=preferences
        )

        db.session.add(new_user)
        db.session.commit()

        # Générer un token JWT pour cet utilisateur
        from src.auth import generate_jwt_token
        token = generate_jwt_token(new_user.id, new_user.name)

        return jsonify({
            'message': 'Inscription réussie', 
            'token': token,
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'preferences': new_user.preferences or {}
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'inscription: {str(e)}'}), 500

@app.route('/api/verify-token', methods=['GET'])
def verify_token():
    """Vérifier la validité d'un token JWT."""
    try:
        # Le middleware vérifie déjà le token et stocke l'utilisateur dans g
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Token invalide'}), 401
            
        # Récupérer les données complètes de l'utilisateur
        user = User.query.get(current_user['user_id'])
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
            
        response_data = {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email or '',
                'preferences': user.preferences or {}
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la vérification: {str(e)}'}), 500

if __name__ == '__main__':
    # Créer les tables de base de données au démarrage
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tables de base de données créées/vérifiées")
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
    
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)

# Exposer l'application pour les serveurs WSGI
application = app