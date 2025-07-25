"""
Base de données pour les utilisateurs.
Ce fichier contient uniquement les données utilisateurs pour le système de recommandation.
"""

# Liste des services de streaming disponibles
STREAMING_SERVICES = [
    "netflix", "amazon", "disney", "hbo", "hulu", "apple", "peacock", "paramount"
]

# Base de données des préférences des utilisateurs
users = [
    {
        "id": 1,
        "name": "Alice",
        "preferences": {
            "genres_likes": ["Science-Fiction", "Thriller", "Animation"],
            "genres_dislikes": ["Horreur", "Guerre"],
            "directors_likes": ["Christopher Nolan", "Quentin Tarantino"],
            "keywords_likes": ["rêve", "voyage", "animaux", "space"],
            "mood_preferences": ["intense", "réflexif", "émouvant"],
            "rating_min": 7.5,
            "streaming_services": ["netflix", "disney"]  # Abonnements aux services de streaming
        },
        "history": []  # Historique vidé car nous n'utilisons plus de base de données locale
    },
    {
        "id": 2,
        "name": "Bob",
        "preferences": {
            "genres_likes": ["Comédie", "Action"],
            "genres_dislikes": ["Drame", "Documentaire"],
            "keywords_likes": ["humour", "aventure", "super-héros"],
            "mood_preferences": ["léger", "drôle", "divertissant"],
            "rating_min": 7.0,
            "streaming_services": ["amazon", "hbo"]  # Abonnements aux services de streaming
        },
        "history": []
    }
]
