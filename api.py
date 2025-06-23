"""
API REST pour le système de recommandation de films et séries.
Ce fichier permet d'exposer les fonctionnalités du système via une API HTTP.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import traceback

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.recommendation_engine import (
    get_recommendations, create_user_profile, update_user_history,
    get_online_genres, reload_users
)
from data.user_database import load_users, save_users, add_user, update_user

app = Flask(__name__)
# Configuration CORS plus permissive pour le développement
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Variable globale pour stocker les utilisateurs
users = []

def refresh_users():
    """Fonction utilitaire pour synchroniser les utilisateurs entre l'API et le moteur de recommandation."""
    global users
    # Utiliser reload_users du moteur de recommandation pour assurer la cohérence
    users = reload_users()
    return users

# Initialiser les utilisateurs au démarrage
refresh_users()

@app.route('/api/users', methods=['GET'])
def get_users():
    """Retourne la liste des utilisateurs."""
    global users
    try:
        # Synchroniser les utilisateurs pour être sûr d'avoir les données à jour
        users = refresh_users()
        
        # Ne pas exposer l'historique et autres données sensibles
        sanitized_users = []
        for user in users:
            try:
                sanitized_user = {
                    'id': user.get('id', 0),
                    'name': user.get('name', 'Utilisateur sans nom'),
                    'preferences': {
                        'genres_likes': user.get('preferences', {}).get('genres_likes', []),
                        'genres_dislikes': user.get('preferences', {}).get('genres_dislikes', []),
                        'keywords_likes': user.get('preferences', {}).get('keywords_likes', []),
                        'rating_min': user.get('preferences', {}).get('rating_min', 7.0),
                        'streaming_services': user.get('preferences', {}).get('streaming_services', [])
                    }
                }
                sanitized_users.append(sanitized_user)
            except Exception as e:
                print(f"Erreur lors de la sanitization d'un utilisateur: {e}")
                # Continuer avec les autres utilisateurs
                continue
        
        return jsonify(sanitized_users)
    except Exception as e:
        print(f"Erreur lors de la récupération des utilisateurs: {e}")
        traceback.print_exc()
        # En cas d'erreur, renvoyer une liste vide mais avec un message
        return jsonify([
            {
                'id': 0,
                'name': 'Erreur de chargement des utilisateurs - Veuillez réessayer',
                'preferences': {'genres_likes': [], 'genres_dislikes': [], 'keywords_likes': [], 'rating_min': 7.0, 'streaming_services': []}
            }
        ])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retourne un utilisateur spécifique."""
    # S'assurer que la liste est à jour
    global users
    users = refresh_users()
    
    for user in users:
        if user['id'] == user_id:
            # Ne pas exposer l'historique
            sanitized_user = {
                'id': user['id'],
                'name': user['name'],
                'preferences': {
                    'genres_likes': user['preferences'].get('genres_likes', []),
                    'genres_dislikes': user['preferences'].get('genres_dislikes', []),
                    'keywords_likes': user['preferences'].get('keywords_likes', []),
                    'rating_min': user['preferences'].get('rating_min', 7.0),
                    'streaming_services': user['preferences'].get('streaming_services', [])
                }
            }
            return jsonify(sanitized_user)
    
    return jsonify({'error': 'Utilisateur non trouvé'}), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    """Crée un nouvel utilisateur."""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Nom d\'utilisateur requis'}), 400
    
    # Créer le profil utilisateur
    new_user = create_user_profile(
        name=data['name'],
        genres_likes=data.get('genres_likes', []),
        genres_dislikes=data.get('genres_dislikes', []),
        directors_likes=data.get('directors_likes', []),
        keywords_likes=data.get('keywords_likes', []),
        mood_preferences=data.get('mood_preferences', []),
        rating_min=data.get('rating_min', 7.0),
        streaming_services=data.get('streaming_services', [])
    )
    
    # Ajouter l'utilisateur à la base de données
    updated_user = add_user(new_user)
    
    # Mettre à jour la liste des utilisateurs en mémoire dans tous les modules
    refresh_users()
    
    return jsonify(updated_user), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user_preferences(user_id):
    """Met à jour les préférences d'un utilisateur."""
    data = request.json
    
    # Synchroniser les utilisateurs pour être sûr d'avoir les données à jour
    global users
    users = refresh_users()
    
    for user in users:
        if user['id'] == user_id:
            # Mettre à jour les préférences
            if 'genres_likes' in data:
                user['preferences']['genres_likes'] = data['genres_likes']
            if 'genres_dislikes' in data:
                user['preferences']['genres_dislikes'] = data['genres_dislikes']
            if 'directors_likes' in data:
                user['preferences']['directors_likes'] = data['directors_likes']
            if 'keywords_likes' in data:
                user['preferences']['keywords_likes'] = data['keywords_likes']
            if 'rating_min' in data:
                user['preferences']['rating_min'] = data['rating_min']
            if 'streaming_services' in data:
                user['preferences']['streaming_services'] = data['streaming_services']
            
            # Sauvegarder les modifications
            if update_user(user):
                # Mettre à jour les listes d'utilisateurs en mémoire dans tous les modules
                refresh_users()
                return jsonify(user)
            else:
                return jsonify({'error': 'Erreur lors de la mise à jour'}), 500
    
    return jsonify({'error': 'Utilisateur non trouvé'}), 404

@app.route('/api/genres', methods=['GET'])
def get_genres():
    """Récupère la liste des genres disponibles."""
    try:
        genres = get_online_genres()
        return jsonify(genres)
    except Exception as e:
        print(f"Erreur lors de la récupération des genres: {e}")
        traceback.print_exc()
        return jsonify({
            'error': f'Erreur lors de la récupération des genres: {str(e)}',
            'genres': ["Action", "Aventure", "Animation", "Comédie", "Crime", 
                       "Documentaire", "Drame", "Famille", "Fantaisie", "Histoire", 
                       "Horreur", "Musique", "Mystère", "Romance", "Science-Fiction", 
                       "Téléfilm", "Thriller", "Guerre", "Western"]
        })

@app.route('/api/services', methods=['GET'])
def get_services():
    """Récupère la liste des services de streaming disponibles."""
    try:
        from data.movies_series_database import STREAMING_SERVICES
        return jsonify(STREAMING_SERVICES)
    except Exception as e:
        print(f"Erreur lors de la récupération des services: {e}")
        traceback.print_exc()
        return jsonify(["netflix", "amazon", "disney", "hbo", "hulu", "apple", "peacock", "paramount"])

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """Récupère des recommandations pour un utilisateur."""
    content_type = request.args.get('content_type', 'all')
    n = int(request.args.get('n', '5'))
    streaming_service = request.args.get('streaming_service', None)
    
    # Vérifier les paramètres
    if content_type not in ['all', 'movies', 'series']:
        content_type = 'all'
    if n < 1:
        n = 5
    elif n > 100:  # Limiter à 100 recommandations maximum
        n = 100
        
    try:
        # S'assurer que les utilisateurs sont synchronisés avant de demander des recommandations
        refresh_users()
        
        recommendations = get_recommendations(
            user_id, 
            n=n, 
            content_type=content_type, 
            streaming_service=streaming_service
        )
        return jsonify(recommendations)
    except Exception as e:
        print(f"Erreur lors de la récupération des recommandations: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la récupération des recommandations: {str(e)}'}), 500

@app.route('/api/history/<int:user_id>/<item_id>', methods=['POST'])
def add_to_history(user_id, item_id):
    """Ajoute un élément à l'historique d'un utilisateur."""
    try:
        if update_user_history(user_id, item_id):
            # Recharger les utilisateurs en mémoire après mise à jour
            refresh_users()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Erreur lors de la mise à jour de l\'historique'}), 500
    except Exception as e:
        print(f"Erreur lors de la mise à jour de l'historique: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la mise à jour de l\'historique: {str(e)}'}), 500

# Endpoint de diagnostic pour aider au débogage
@app.route('/api/status', methods=['GET'])
def api_status():
    """Vérifie l'état de l'API et retourne des informations de diagnostic."""
    try:
        status = {
            "status": "ok",
            "user_count": len(users),
            "users_loaded": len(users) > 0,
            "user_ids": [user.get('id') for user in users[:10]],  # Afficher les 10 premiers IDs
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
