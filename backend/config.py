"""
Configuration du système de recommandation.
Ce fichier stocke les informations de configuration comme les clés API (administrateur uniquement).
"""

# Clé API pour TMDb (The Movie Database)
# Cette clé est gérée par l'administrateur et utilisée pour toutes les requêtes
# Ne partagez pas cette clé avec les utilisateurs finaux
TMDB_API_KEY = "f584c416fc7b0c9c1591acabafc13a72"

# Clé API pour Watchmode directe
# Obtenez votre clé sur https://api.watchmode.com/
WATCHMODE_API_KEY = "TKWcnrMlv79TRBrYvnkBNO44m8h7NOLK7xSUONTj"

# Clé API pour Watchmode via RapidAPI (non utilisée)
RAPIDAPI_KEY = ""

# Configuration des fournisseurs d'API
API_PROVIDERS = {
    "tmdb": {
        "enabled": True,
        "priority": 1,  # Plus le nombre est bas, plus la priorité est haute
        "timeout": 10,
        "api_key": TMDB_API_KEY,
        "base_url": "https://api.themoviedb.org/3"
    },
    "watchmode": {
        "enabled": bool(WATCHMODE_API_KEY),  # Activé si clé Watchmode directe disponible  
        "priority": 2,
        "timeout": 10,
        "api_key": WATCHMODE_API_KEY,
        "base_url": "https://api.watchmode.com/v1",
        "type": "direct"
    }
}
