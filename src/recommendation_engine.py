"""
Moteur de recommandation pour films et séries.
Ce fichier contient les algorithmes pour recommander des films et séries en fonction des préférences des utilisateurs.
La recherche est effectuée en ligne via l'API TMDb.
"""

import sys
import os
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer la base de données des utilisateurs
from data.movies_series_database import STREAMING_SERVICES
from data.user_database import load_users, update_user

# Charger la liste des utilisateurs
users = load_users()

# Importer la clé API depuis le fichier de configuration
# La clé est définie par l'administrateur et utilisée pour toutes les requêtes
try:
    from config import TMDB_API_KEY
except ImportError:
    # Si le fichier n'existe pas, utiliser une valeur par défaut
    TMDB_API_KEY = "f584c416fc7b0c9c1591acabafc13a72"

TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Ces variables ne sont plus nécessaires car nous utilisons une clé API centralisée
# _api_key_warning_shown = False
# _user_provided_api_key = None

# Cette fonction est supprimée car nous utilisons maintenant une clé API centralisée gérée par l'administrateur

def check_api_key(force_ask=False):
    """
    Vérifie si la clé API est valide.
    
    Args:
        force_ask: Ce paramètre est conservé pour compatibilité mais n'est plus utilisé
                   car la clé API est maintenant gérée centralement.
    """
    # La clé API est maintenant toujours définie par l'administrateur du système
    # et ne peut pas être modifiée par les utilisateurs finaux
    return True

def search_online(query, content_type="movie"):
    """
    Recherche des films ou séries en ligne en utilisant l'API TMDb.
    
    Args:
        query: La requête de recherche
        content_type: "movie" ou "tv" (pour les séries)
        
    Returns:
        Liste des résultats de recherche
    """
    # La clé API est gérée par l'administrateur et toujours disponible
        
    endpoint = f"{TMDB_BASE_URL}/search/{content_type}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "fr-FR",
        "query": query,
        "page": 1,
        "include_adult": False
    }
    
    try:
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return results
        else:
            print(f"Erreur lors de la recherche: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception lors de la recherche: {e}")
        return []

def get_movie_details(movie_id):
    """
    Obtient les détails d'un film à partir de l'API TMDb.
    
    Args:
        movie_id: ID TMDb du film
        
    Returns:
        Détails du film
    """
    # La clé API est gérée par l'administrateur et toujours disponible
        
    endpoint = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "fr-FR",
        "append_to_response": "credits,keywords,watch/providers"
    }
    
    try:
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur lors de la récupération des détails du film: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Exception lors de la récupération des détails du film: {e}")
        return {}

def get_tv_details(tv_id):
    """
    Obtient les détails d'une série à partir de l'API TMDb.
    
    Args:
        tv_id: ID TMDb de la série
        
    Returns:
        Détails de la série
    """
    # La clé API est gérée par l'administrateur et toujours disponible
        
    endpoint = f"{TMDB_BASE_URL}/tv/{tv_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "fr-FR",
        "append_to_response": "credits,keywords,watch/providers"
    }
    
    try:
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur lors de la récupération des détails de la série: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Exception lors de la récupération des détails de la série: {e}")
        return {}

def get_genre_list(content_type="movie"):
    """
    Obtient la liste des genres de films ou séries à partir de l'API TMDb.
    
    Args:
        content_type: "movie" ou "tv" (pour les séries)
        
    Returns:
        Dictionnaire des genres {id: nom}
    """    # La clé API est gérée par l'administrateur et toujours disponible
        
    endpoint = f"{TMDB_BASE_URL}/genre/{content_type}/list"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "fr-FR"
    }
    
    genre_dict = {}
    try:
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            genres = response.json().get("genres", [])
            for genre in genres:
                genre_dict[genre["id"]] = genre["name"]
        return genre_dict
    except Exception as e:
        print(f"Exception lors de la récupération des genres: {e}")
        return {}

def get_online_genres():
    """
    Retourne tous les genres disponibles depuis l'API TMDb.
    
    Returns:
        Liste des genres de films et séries disponibles
    """
    movie_genres = get_genre_list("movie")
    tv_genres = get_genre_list("tv")
    
    # Fusionner les deux listes de genres et éliminer les doublons
    all_genres = set()
    for genre_name in movie_genres.values():
        all_genres.add(genre_name)
    for genre_name in tv_genres.values():
        all_genres.add(genre_name)
    
    return sorted(list(all_genres))

def get_recommendations_online(user_preferences, max_results=10, content_type="all", streaming_service=None):
    """
    Obtient des recommandations en ligne basées sur les préférences de l'utilisateur.
    
    Args:
        user_preferences: Préférences de l'utilisateur
        max_results: Nombre maximum de résultats à retourner
        content_type: "movie", "tv", ou "all"
        streaming_service: Service de streaming spécifique (optionnel)
        
    Returns:
        Liste des recommandations
    """
    # La clé API est gérée par l'administrateur et toujours disponible
        
    recommendations = []
    
    # Récupérer les genres disponibles
    movie_genres = get_genre_list("movie")
    tv_genres = get_genre_list("tv")
    
    # Convertir les genres préférés en IDs TMDb
    preferred_genre_ids = []
    for genre_name in user_preferences.get("genres_likes", []):
        for genre_id, name in movie_genres.items():
            if name.lower() == genre_name.lower():
                preferred_genre_ids.append(genre_id)
                break
    
    # Si aucun genre préféré n'est trouvé, utiliser des genres populaires
    if not preferred_genre_ids:
        # Action, Adventure, Science Fiction, Fantasy, Animation
        preferred_genre_ids = [28, 12, 878, 14, 16]
    
    # Faire des recherches pour chaque genre préféré
    all_results = []
      # Rechercher des films (amélioré)
    if content_type in ["movie", "movies", "all"]:
        # Paramètres généraux plus stricts pour garantir des films de qualité
        min_rating = max(user_preferences.get("rating_min", 7.0), 7.0)  # Au moins 7.0 de note moyenne
        min_votes = 100  # Au moins 100 votes pour éviter les films peu connus ou mal évalués
        
        # Chercher par genre préféré
        for genre_id in preferred_genre_ids:
            # Chercher des films populaires
            endpoint = f"{TMDB_BASE_URL}/discover/movie"
            params = {
                "api_key": TMDB_API_KEY,
                "language": "fr-FR",
                "sort_by": "popularity.desc",
                "with_genres": str(genre_id),
                "vote_average.gte": min_rating,
                "vote_count.gte": min_votes,
                "page": 1
            }
            
            try:
                response = requests.get(endpoint, params=params)
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    for result in results:
                        result["media_type"] = "movie"
                    all_results.extend(results)
            except Exception as e:
                print(f"Exception lors de la découverte de films populaires: {e}")
            
            # Chercher les films les mieux notés (pas juste les plus populaires)
            params["sort_by"] = "vote_average.desc"
            params["vote_count.gte"] = 500  # Plus de votes pour garantir des films vraiment bons
            
            try:
                response = requests.get(endpoint, params=params)
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    for result in results:
                        result["media_type"] = "movie"
                    all_results.extend(results)
            except Exception as e:
                print(f"Exception lors de la découverte de films bien notés: {e}")
      # Rechercher des séries (amélioré)
    if content_type in ["tv", "series", "all"]:
        # Paramètres généraux plus stricts pour garantir des séries de qualité
        min_rating = max(user_preferences.get("rating_min", 7.0), 7.0)
        min_votes = 100
        
        for genre_id in preferred_genre_ids:
            # Chercher des séries populaires
            endpoint = f"{TMDB_BASE_URL}/discover/tv"
            params = {
                "api_key": TMDB_API_KEY,
                "language": "fr-FR",
                "sort_by": "popularity.desc",
                "with_genres": str(genre_id),
                "vote_average.gte": min_rating,
                "vote_count.gte": min_votes,
                "page": 1
            }
            
            try:
                response = requests.get(endpoint, params=params)
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    for result in results:
                        result["media_type"] = "tv"
                    all_results.extend(results)
            except Exception as e:
                print(f"Exception lors de la découverte de séries populaires: {e}")
                
            # Chercher les séries les mieux notées
            params["sort_by"] = "vote_average.desc"
            params["vote_count.gte"] = 200
            
            try:
                response = requests.get(endpoint, params=params)
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    for result in results:
                        result["media_type"] = "tv"
                    all_results.extend(results)
            except Exception as e:
                print(f"Exception lors de la découverte de séries bien notées: {e}")
      # Récupérer plus de détails pour les résultats les plus pertinents
    # et calculer un score de pertinence
    # Amélioration: Tri initial plus équilibré entre note, popularité et diversité
    # Pour éviter de toujours voir les mêmes films très populaires
    
    # Supprimer les doublons éventuels (même ID)
    unique_results = []
    seen_ids = set()
    for result in all_results:
        result_id = result.get("id")
        if result_id not in seen_ids:
            seen_ids.add(result_id)
            unique_results.append(result)
    
    # Diversifier les résultats en tenant compte de la note et de la popularité de manière plus équilibrée
    top_results = sorted(
        unique_results, 
        key=lambda x: (
            x.get("vote_average", 0) * 1.5 +  # Plus d'importance à la note
            min(x.get("popularity", 0) / 200, 3)  # Limiter davantage l'impact de la popularité
        ), 
        reverse=True
    )[:max_results*3]  # Augmenter le pool de résultats pour plus de diversité
    
    # Fonction pour traiter chaque résultat et récupérer plus de détails
    def process_result(result):
        result_id = result.get("id")
        media_type = result.get("media_type")
        
        if media_type == "movie":
            details = get_movie_details(result_id)
        else:  # tv
            details = get_tv_details(result_id)
        
        if not details:
            return None
        
        # Calculer un score de correspondance
        score = 0
          # Score basé sur la popularité et la note (amélioré)
        # Les films avec une meilleure note auront maintenant un impact plus grand
        vote_average = details.get("vote_average", 0)
        vote_count = details.get("vote_count", 0)
        
        # Privilégier les films bien notés avec beaucoup d'évaluations
        if vote_count > 100:
            score += vote_average * 1.0  # Double importance pour les films bien évalués
        else:
            score += vote_average * 0.5
            
        # Limiter l'impact de la popularité mais toujours la considérer
        score += min(details.get("popularity", 0) / 100, 3)
          # Score basé sur les genres (amélioré)
        user_genre_likes = [g.lower() for g in user_preferences.get("genres_likes", [])]
        user_genre_dislikes = [g.lower() for g in user_preferences.get("genres_dislikes", [])]
        
        # Ajouter une pénalité si aucun genre aimé n'est présent
        genres_matched = False
        
        if media_type == "movie":
            genre_dict = movie_genres
        else:
            genre_dict = tv_genres
        
        # Compter le nombre total de genres présents dans le film/série
        total_genres = len(details.get("genres", []))
        matching_genres = 0
        disliked_genres = 0
            
        for genre_id in details.get("genres", []):
            genre_name = genre_dict.get(genre_id.get("id", 0), "").lower()
            
            if genre_name in user_genre_likes:
                matching_genres += 1
                genres_matched = True
                score += 3  # Augmenté de 2 à 3
                
            if genre_name in user_genre_dislikes:
                disliked_genres += 1
                score -= 4  # Augmenté de 3 à 4
        
        # Si plus de la moitié des genres sont aimés, bonus supplémentaire
        if total_genres > 0 and matching_genres / total_genres > 0.5:
            score += 2
            
        # Si aucun genre aimé n'est trouvé, pénalité
        if user_genre_likes and not genres_matched:
            score -= 2
          # Score basé sur les mots-clés (amélioré)
        user_keywords = [k.lower() for k in user_preferences.get("keywords_likes", [])]
        matched_keywords = 0
        
        if "keywords" in details:
            for keyword in details["keywords"].get("keywords", []):
                keyword_name = keyword.get("name", "").lower()
                for user_keyword in user_keywords:
                    # Correspondance exacte ou partielle
                    if user_keyword in keyword_name or keyword_name in user_keyword:
                        score += 2.0  # Augmenté de 1.5 à 2.0
                        matched_keywords += 1
                        break
        
        # Bonus pour correspondance de plusieurs mots-clés
        if matched_keywords > 1:
            score += matched_keywords * 0.5  # Bonus supplémentaire par mot-clé correspondant
            
        # Score basé sur les réalisateurs/créateurs préférés
        user_directors = [d.lower() for d in user_preferences.get("directors_likes", [])]
        if "credits" in details and "crew" in details["credits"]:
            if media_type == "movie":
                directors = [person["name"].lower() for person in details["credits"]["crew"] if person["job"] == "Director"]
                for director in directors:
                    for user_director in user_directors:
                        if user_director in director:
                            score += 4.0  # Fort bonus pour un réalisateur préféré
                            break
            else:  # tv
                creators = [person["name"].lower() for person in details.get("created_by", [])]
                for creator in creators:
                    for user_director in user_directors:
                        if user_director in creator:
                            score += 4.0  # Fort bonus pour un créateur préféré
                            break
        
        # Récupérer les informations de streaming (watch/providers)
        streaming_services = []
        if "watch/providers" in details and "results" in details["watch/providers"]:
            providers_fr = details["watch/providers"].get("results", {}).get("FR", {})
            if "flatrate" in providers_fr:
                for provider in providers_fr["flatrate"]:
                    provider_name = provider.get("provider_name", "").lower()
                    if "netflix" in provider_name:
                        streaming_services.append("netflix")
                    elif "disney" in provider_name:
                        streaming_services.append("disney")
                    elif "amazon" in provider_name or "prime" in provider_name:
                        streaming_services.append("amazon")
                    elif "hbo" in provider_name:
                        streaming_services.append("hbo")
                    elif "hulu" in provider_name:
                        streaming_services.append("hulu")
                    elif "apple" in provider_name:
                        streaming_services.append("apple")
                    elif "peacock" in provider_name:
                        streaming_services.append("peacock")
                    elif "paramount" in provider_name:
                        streaming_services.append("paramount")
        
        # Si un service de streaming spécifique est demandé et que le contenu n'est pas disponible
        # sur ce service, ne pas inclure dans les recommandations
        if streaming_service and streaming_service.lower() not in streaming_services:
            return None
              # Si l'utilisateur a demandé de filtrer par ses services d'abonnement
        user_streaming_services = user_preferences.get("streaming_services", [])
        if user_preferences.get("filter_by_user_services", False) and user_streaming_services:
            # Vérifier si le contenu est disponible sur au moins un des services de l'utilisateur
            if not any(service in streaming_services for service in user_streaming_services):
                return None
            else:
                # Bonus de score en fonction du nombre de services disponibles
                matching_services = sum(1 for service in user_streaming_services if service in streaming_services)
                score += matching_services * 1.5  # Augmenté et proportionnel au nombre de services
        
        # Construire l'objet de recommandation
        recommendation = {
            "item": {
                "id": details.get("id"),
                "title": details.get("title", details.get("name", "Sans titre")),
                "genre": [genre["name"] for genre in details.get("genres", [])],
                "year": details.get("release_date", details.get("first_air_date", ""))[:4] if details.get("release_date", details.get("first_air_date", "")) else "",
                "rating": details.get("vote_average", 0),
                "plot": details.get("overview", "Pas de synopsis disponible"),
                "poster_path": details.get("poster_path"),
                "backdrop_path": details.get("backdrop_path")
            },
            "score": score,
            "type": "movie" if media_type == "movie" else "series",
            "streaming_services": streaming_services
        }
        
        # Ajouter le réalisateur/créateur si disponible
        if "credits" in details and "crew" in details["credits"]:
            if media_type == "movie":
                directors = [person["name"] for person in details["credits"]["crew"] if person["job"] == "Director"]
                if directors:
                    recommendation["item"]["director"] = ", ".join(directors)
            else:  # tv
                creators = [person["name"] for person in details.get("created_by", [])]
                if creators:
                    recommendation["item"]["creator"] = ", ".join(creators)
        
        return recommendation
    
    # Utiliser ThreadPoolExecutor pour paralléliser les requêtes
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_result, top_results))
      # Filtrer les résultats None et trier par score
    recommendations = [r for r in results if r]
    
    # Filtrer les éléments déjà vus dans l'historique de l'utilisateur
    user_history = user_preferences.get('history', [])
    if user_history:
        recommendations = [r for r in recommendations if str(r["item"]["id"]) not in [str(h) for h in user_history]]
    
    # Trier par score
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    
    # Si nous n'avons pas assez de recommandations, élargir les critères
    if len(recommendations) < max_results:
        print("\nRecherche de recommandations supplémentaires...")
        # On pourrait implémenter une recherche supplémentaire ici
    
    return recommendations[:max_results]

def get_recommendations(user_id, n=5, content_type='all', streaming_service=None):
    """
    Obtient des recommandations de films et/ou séries pour un utilisateur en fonction de ses préférences.
    Utilise l'API TMDb pour obtenir des recommandations en ligne.
    
    Args:
        user_id: ID de l'utilisateur
        n: Nombre de recommandations à retourner
        content_type: 'movies', 'series', ou 'all'
        streaming_service: Service de streaming spécifique (optionnel)
        
    Returns:
        Liste des recommandations avec leurs scores et disponibilité en streaming
    """
    # Trouver l'utilisateur
    user = None
    for u in users:
        if u['id'] == user_id:
            user = u
            break
    
    if not user:
        return []
    
    user_preferences = user.get('preferences', {})
    user_preferences['history'] = user.get('history', [])
    
    # Convertir le type de contenu pour la compatibilité avec l'API TMDb
    content_type_map = {
        'movies': 'movie',
        'series': 'tv',
        'all': 'all'
    }
    online_content_type = content_type_map.get(content_type, 'all')
    
    # Si aucun service de streaming n'est spécifié mais que l'utilisateur a des abonnements,
    # on peut demander s'il veut filtrer par ses services
    user_streaming_services = user_preferences.get('streaming_services', [])
    
    if not streaming_service and user_streaming_services:
        print("\nVous êtes abonné(e) aux services suivants:", 
              ", ".join(s.capitalize() for s in user_streaming_services))
        filter_option = input("Voulez-vous voir uniquement les contenus disponibles sur vos abonnements? (o/n): ")
        if filter_option.lower() in ['o', 'oui', 'y', 'yes']:
            # On ne spécifie pas de service précis, le filtrage se fera au niveau des résultats
            # pour inclure tous les services de l'utilisateur
            print("Filtrage activé pour vos services d'abonnement.")
            user_preferences['filter_by_user_services'] = True
        else:
            user_preferences['filter_by_user_services'] = False
    
    # Utiliser la recherche en ligne
    recommendations = get_recommendations_online(
        user_preferences, 
        max_results=n, 
        content_type=online_content_type,
        streaming_service=streaming_service
    )
    
    return recommendations

def create_user_profile(name, genres_likes=[], genres_dislikes=[], directors_likes=[], 
                        keywords_likes=[], mood_preferences=[], rating_min=7.0, streaming_services=[]):
    """
    Crée un nouveau profil utilisateur.
    
    Args:
        name: Nom de l'utilisateur
        genres_likes: Genres préférés
        genres_dislikes: Genres non appréciés
        directors_likes: Réalisateurs/créateurs préférés
        keywords_likes: Mots-clés d'intérêt
        mood_preferences: Ambiances préférées
        rating_min: Note minimale pour les recommandations
        streaming_services: Liste des services de streaming auxquels l'utilisateur est abonné
    
    Returns:
        Le profil utilisateur créé
    """
    new_id = max([user['id'] for user in users]) + 1 if users else 1
    
    new_user = {
        "id": new_id,
        "name": name,
        "preferences": {
            "genres_likes": genres_likes,
            "genres_dislikes": genres_dislikes,
            "directors_likes": directors_likes,
            "keywords_likes": keywords_likes,
            "mood_preferences": mood_preferences,
            "rating_min": rating_min,
            "streaming_services": streaming_services
        },
        "history": []
    }
      # Ne pas ajouter directement à la liste users
    # La gestion de la base de données est maintenant faite dans user_database.py
    # et l'ajout est fait dans user_interface.py
    return new_user

def update_user_history(user_id, item_id):
    """
    Met à jour l'historique d'un utilisateur après qu'il ait regardé un film/série.
    Sauvegarde les changements dans la base de données persistante.
    """
    # Recharger les utilisateurs pour avoir les données les plus récentes
    current_users = load_users()
    
    for user in current_users:
        if user['id'] == user_id:
            if 'history' not in user:
                user['history'] = []
            
            if item_id not in user['history']:
                user['history'].append(item_id)
                
            # Mettre à jour la liste des utilisateurs globalement
            for i, u in enumerate(users):
                if u['id'] == user_id:
                    users[i] = user
                    break
            
            # Sauvegarder les changements dans la base de données
            return update_user(user)
            
    return False

def configure_api_key():
    """
    Cette fonction est conservée pour compatibilité mais n'est plus utilisée,
    car la clé API est maintenant gérée centralement par l'administrateur.
    
    Returns:
        bool: True si la configuration a réussi, False sinon
    """
    print("\n=== CONFIGURATION DE LA CLÉ API TMDb ===")
    print("✅ La clé API est déjà configurée par l'administrateur du système.")
    print("Vous n'avez pas besoin de fournir votre propre clé API.")
    return True
