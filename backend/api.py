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
from src.auth_routes import auth_bp
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

# Enregistrer les routes d'authentification
app.register_blueprint(auth_bp)

# Gestionnaire d'erreur pour l'authentification
app.register_error_handler(AuthError, handle_auth_error)

# Note: Les utilisateurs sont maintenant gérés par SQLAlchemy via la classe User

@app.route('/api/users', methods=['GET'])
def get_users():
    """Retourne la liste des utilisateurs (pour admin seulement)."""
    # Cette route pourrait être limitée aux administrateurs
    # Pour l'instant, on retourne une liste vide pour des raisons de sécurité
    return jsonify([])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retourne un utilisateur spécifique."""
    try:
        # Vérifier que l'utilisateur connecté peut accéder à ce profil
        if not check_user_access(user_id):
            return jsonify({'error': 'Accès non autorisé à ce compte'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Ne pas exposer l'historique et les informations d'authentification
        sanitized_user = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'preferences': {
                'genres_likes': user.preferences.get('genres_likes', []) if user.preferences else [],
                'genres_dislikes': user.preferences.get('genres_dislikes', []) if user.preferences else [],
                'keywords_likes': user.preferences.get('keywords_likes', []) if user.preferences else [],
                'rating_min': user.preferences.get('rating_min', 7.0) if user.preferences else 7.0,
                'streaming_services': user.preferences.get('streaming_services', []) if user.preferences else []
            }
        }
        return jsonify(sanitized_user)
        
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération de l\'utilisateur: {str(e)}'}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Crée un nouvel utilisateur (désactivé - utiliser /api/register)."""
    return jsonify({'error': 'Utiliser /api/register pour créer un compte'}), 400

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
        streaming_service = request.args.get('streaming_service', None)
        
        # Vérifier les paramètres
        if content_type not in ['all', 'movies', 'series']:
            content_type = 'all'
        if n < 1 or n > 20:  # Limiter le nombre de recommandations
            n = 5
            
        recommendations = modular_engine.get_recommendations(
            user_id, 
            n=n, 
            content_type=content_type, 
            streaming_service=streaming_service
        )
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération des recommandations: {str(e)}'}), 500

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

        name = data.get('username')
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

        return jsonify({'message': 'Inscription réussie', 'user': {
            'id': new_user.id,
            'name': new_user.name,
            'email': new_user.email,
            'preferences': new_user.preferences
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'inscription: {str(e)}'}), 500

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