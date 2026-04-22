"""
API REST pour le système de recommandation de films et séries.
Expose les fonctionnalités du système via une API HTTP.
"""

import os
import sys

# Forcer UTF-8 pour stdout/stderr sous Windows (evite UnicodeEncodeError sur emojis)
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash

# Ajouter le répertoire courant au chemin pour pouvoir importer les modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.recommendation_engine_v2 import modular_engine
from models import db, User
from src.middleware import (
    init_auth_middleware,
    check_user_access,
    get_current_user,
    AuthError,
    handle_auth_error,
)
from src.auth import generate_jwt_token, verify_password

# Configuration des fichiers statiques pour le frontend
static_folder = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, static_folder=static_folder, static_url_path='')

# Configuration CORS pour développement local (Vue CLI sur 8080, Flask sur 5000)
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
    ]}},
    supports_credentials=True
)

# Configuration SQLAlchemy - SQLite local (aucune installation requise)
db_path = os.path.join(backend_dir, 'data', 'whattowatch.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
init_auth_middleware(app)
app.register_error_handler(AuthError, handle_auth_error)


def init_database():
    """Crée les tables SQLite si elles n'existent pas encore."""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Base de données SQLite initialisée")
        except Exception as e:
            print(f"❌ Erreur init base: {e}")


init_database()


# ===== ENDPOINTS PUBLICS =====

@app.route('/api/ping', methods=['GET'])
def ping():
    """Endpoint simple pour tester que l'API fonctionne."""
    return jsonify({
        'status': 'ok',
        'message': 'WhatToWatch API is running',
        'version': '2.0'
    })


@app.route('/api/login', methods=['POST'])
def login_user():
    """Connexion utilisateur avec email et mot de passe."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Données JSON manquantes'}), 400

        email = (data.get('email') or '').strip()
        password = data.get('password') or ''

        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400

        user = User.query.filter_by(email=email).first()
        # Message générique pour ne pas divulguer si l'email existe
        if not user or not verify_password(password, user.password_hash, user.password_salt or ''):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

        token = generate_jwt_token(user.id, user.name)

        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email or '',
                'preferences': user.preferences or {}
            }
        })

    except Exception as e:
        app.logger.exception("Erreur lors du login")
        return jsonify({'error': f'Erreur lors de la connexion: {str(e)}'}), 500


@app.route('/api/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Données JSON manquantes'}), 400

        name = (data.get('username') or data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        preferences = data.get('preferences', {}) or {}

        # Validation
        if not name or not email or not password:
            return jsonify({'error': 'Nom, email et mot de passe requis'}), 400
        if '@' not in email:
            return jsonify({'error': 'Adresse email invalide'}), 400
        if len(password) < 6:
            return jsonify({'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        if len(name) < 3:
            return jsonify({'error': "Le nom d'utilisateur doit contenir au moins 3 caractères"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Un compte avec cet email existe déjà'}), 409

        password_hash = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            password_salt="",  # werkzeug intègre le salt dans le hash
            preferences=preferences
        )

        db.session.add(new_user)
        db.session.commit()

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
        app.logger.exception("Erreur lors de l'inscription")
        return jsonify({'error': f"Erreur lors de l'inscription: {str(e)}"}), 500


@app.route('/api/genres', methods=['GET'])
def get_genres():
    """Liste des genres disponibles."""
    genres = [
        "Action", "Aventure", "Animation", "Comédie", "Crime",
        "Documentaire", "Drame", "Famille", "Fantaisie", "Histoire",
        "Horreur", "Musique", "Mystère", "Romance", "Science-Fiction",
        "Thriller", "Guerre", "Western"
    ]
    return jsonify(genres)


@app.route('/api/services', methods=['GET'])
def get_services():
    """Liste des services de streaming disponibles."""
    from data.movies_series_database import STREAMING_SERVICES
    return jsonify(STREAMING_SERVICES)


# ===== ENDPOINTS AUTHENTIFIÉS =====

@app.route('/api/logout', methods=['POST'])
def logout():
    """Déconnexion (JWT stateless — le client supprime simplement le token)."""
    return jsonify({'message': 'Déconnexion réussie'}), 200


@app.route('/api/verify-token', methods=['GET'])
def verify_token():
    """Vérifie la validité du token et retourne les infos utilisateur."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Token invalide'}), 401

    user = User.query.get(current_user['user_id'])
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email or '',
            'preferences': user.preferences or {}
        }
    })


@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Change le mot de passe de l'utilisateur connecté."""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentification requise'}), 401

        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400

        current_password = data.get('current_password') or ''
        new_password = data.get('new_password') or ''

        if not current_password or not new_password:
            return jsonify({'error': 'Mot de passe actuel et nouveau requis'}), 400
        if len(new_password) < 6:
            return jsonify({'error': 'Le nouveau mot de passe doit contenir au moins 6 caractères'}), 400

        user = User.query.get(current_user['user_id'])
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        if not verify_password(current_password, user.password_hash, user.password_salt or ''):
            return jsonify({'error': 'Mot de passe actuel incorrect'}), 401

        user.password_hash = generate_password_hash(new_password)
        user.password_salt = ""
        db.session.commit()

        return jsonify({'message': 'Mot de passe modifié avec succès'})

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Erreur changement mot de passe")
        return jsonify({'error': f'Erreur: {str(e)}'}), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retourne les informations de l'utilisateur (propriétaire uniquement)."""
    if not check_user_access(user_id):
        return jsonify({'error': 'Accès non autorisé à ce compte'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    preferences = user.preferences or {}
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'preferences': preferences,
        'watch_history': preferences.get('watch_history', [])
    })


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user_preferences(user_id):
    """Met à jour les préférences de l'utilisateur."""
    if not check_user_access(user_id):
        return jsonify({'error': 'Accès non autorisé à ce compte'}), 403

    try:
        data = request.get_json(silent=True) or {}

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        if user.preferences is None:
            user.preferences = {}

        if 'name' in data and data['name']:
            user.name = data['name']

        # Champs autorisés à être mis à jour
        allowed_prefs = [
            'genres_likes', 'genres_dislikes', 'directors_likes',
            'keywords_likes', 'mood_preferences', 'rating_min',
            'streaming_services'
        ]
        for key in allowed_prefs:
            if key in data:
                user.preferences[key] = data[key]

        # Forcer SQLAlchemy à détecter la mutation du champ JSON
        user.preferences = dict(user.preferences)

        db.session.commit()

        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'preferences': user.preferences
        })

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Erreur mise à jour utilisateur")
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500


@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """Récupère des recommandations pour un utilisateur."""
    if not check_user_access(user_id):
        return jsonify({'error': 'Accès non autorisé à ce compte'}), 403

    try:
        content_type = request.args.get('content_type', 'all')
        try:
            n = int(request.args.get('n', '5'))
        except ValueError:
            n = 5

        # Support flexible pour streaming services
        streaming_services = None
        param = request.args.get('streaming_services') or request.args.get('streaming_service')
        if param:
            streaming_services = [s.strip() for s in param.split(',') if s.strip()]

        if content_type not in ('all', 'movies', 'series'):
            content_type = 'all'
        if n < 1 or n > 20:
            n = 5

        recommendations = modular_engine.get_recommendations(
            user_id,
            n=n,
            content_type=content_type,
            streaming_services=streaming_services
        )

        return jsonify(recommendations)

    except Exception as e:
        app.logger.exception("Erreur recommandations")
        return jsonify({'error': f'Erreur lors de la récupération des recommandations: {str(e)}'}), 500


@app.route('/api/users/<int:user_id>/history', methods=['POST'])
def add_to_user_history(user_id):
    """Ajoute un élément à l'historique d'un utilisateur."""
    if not check_user_access(user_id):
        return jsonify({'error': 'Accès non autorisé à ce compte'}), 403

    try:
        data = request.get_json(silent=True) or {}
        item = data.get('item', {})
        if not item or not item.get('id'):
            return jsonify({'error': 'Item invalide'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        if user.preferences is None:
            user.preferences = {}
        if 'watch_history' not in user.preferences:
            user.preferences['watch_history'] = []

        history = user.preferences['watch_history']
        already_present = any(
            h.get('id') == item.get('id') and h.get('content_type') == item.get('content_type')
            for h in history
        )
        if not already_present:
            history.append(item)
            user.preferences = dict(user.preferences)
            db.session.commit()

        return jsonify({'success': True, 'message': 'Ajouté à l\'historique'})

    except Exception as e:
        db.session.rollback()
        app.logger.exception("Erreur ajout historique")
        return jsonify({'error': f"Erreur: {str(e)}"}), 500


@app.route('/api/search', methods=['GET'])
def search_content():
    """Recherche de contenu via les APIs multiples."""
    try:
        if not get_current_user():
            return jsonify({'error': 'Authentification requise'}), 401

        query = (request.args.get('q') or '').strip()
        content_type = request.args.get('type', 'all')
        try:
            max_results = int(request.args.get('limit', 20))
        except ValueError:
            max_results = 20

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

    except Exception as e:
        app.logger.exception("Erreur recherche")
        return jsonify({'error': f'Erreur lors de la recherche: {str(e)}'}), 500


@app.route('/api/trending', methods=['GET'])
def get_trending_content():
    """Récupère le contenu tendance."""
    try:
        if not get_current_user():
            return jsonify({'error': 'Authentification requise'}), 401

        content_type = request.args.get('type', 'all')
        try:
            max_results = int(request.args.get('limit', 20))
        except ValueError:
            max_results = 20

        if max_results < 1 or max_results > 50:
            max_results = 20

        results = modular_engine.get_trending_content(
            content_type=content_type,
            max_results=max_results
        )
        return jsonify(results)

    except Exception as e:
        app.logger.exception("Erreur tendances")
        return jsonify({'error': f'Erreur: {str(e)}'}), 500


@app.route('/api/streaming-services', methods=['GET'])
def get_streaming_services():
    """Services de streaming supportés."""
    if not get_current_user():
        return jsonify({'error': 'Authentification requise'}), 401
    services = modular_engine.get_supported_streaming_services()
    return jsonify({
        'supported_services': services,
        'total_services': len(services)
    })


@app.route('/api/providers', methods=['GET'])
def get_api_providers():
    """État des fournisseurs d'API."""
    try:
        status = modular_engine.get_api_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': f'Erreur: {str(e)}'}), 500


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Vide le cache système (utilisateur authentifié)."""
    if not get_current_user():
        return jsonify({'error': 'Authentification requise'}), 401
    modular_engine.clear_cache()
    return jsonify({'success': True, 'message': 'Cache vidé avec succès'})


# ===== ROUTES FRONTEND (SPA) =====

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Sert les fichiers du frontend Vue.js (fallback SPA sur index.html)."""
    if path and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)

    index_path = os.path.join(static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)

    return jsonify({
        'message': 'WhatToWatch API is running',
        'status': 'Frontend not built yet - run build script first'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Démarrage local sur http://127.0.0.1:{port}")
    app.run(debug=True, host='127.0.0.1', port=port)
