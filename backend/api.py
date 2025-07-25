"""
API REST pour le système de recommandation de films et séries.
Ce fichier permet d'exposer les fonctionnalités du système via une API HTTP.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.recommendation_engine import (
    get_recommendations, create_user_profile, update_user_history,
    get_online_genres
)
from data.user_database import load_users, save_users, add_user, update_user

app = Flask(__name__)
CORS(app)  # Activer CORS pour permettre les requêtes depuis le frontend

# Charger les utilisateurs au démarrage
users = load_users()

@app.route('/api/users', methods=['GET'])
def get_users():
    """Retourne la liste des utilisateurs."""
    # Ne pas exposer l'historique et autres données sensibles
    sanitized_users = []
    for user in users:
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
        sanitized_users.append(sanitized_user)
    
    return jsonify(sanitized_users)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retourne un utilisateur spécifique."""
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
    
    # Mettre à jour la liste des utilisateurs en mémoire
    global users
    users = load_users()
    
    return jsonify(updated_user), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user_preferences(user_id):
    """Met à jour les préférences d'un utilisateur."""
    data = request.json
    
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

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """Récupère des recommandations pour un utilisateur."""
    content_type = request.args.get('content_type', 'all')
    n = int(request.args.get('n', '5'))
    streaming_service = request.args.get('streaming_service', None)
    
    # Vérifier les paramètres
    if content_type not in ['all', 'movies', 'series']:
        content_type = 'all'
    if n < 1 or n > 20:  # Limiter le nombre de recommandations
        n = 5
        
    try:
        recommendations = get_recommendations(
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
    if update_user_history(user_id, item_id):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Erreur lors de la mise à jour de l\'historique'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
