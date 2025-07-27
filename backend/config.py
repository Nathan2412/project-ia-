"""
Configuration du système de recommandation.
Ce fichier stocke les informations de configuration comme les clés API (administrateur uniquement).
"""

# Clé API pour TMDb (The Movie Database)
# Cette clé est gérée par l'administrateur et utilisée pour toutes les requêtes
# Ne partagez pas cette clé avec les utilisateurs finaux
TMDB_API_KEY = "f584c416fc7b0c9c1591acabafc13a72"

# Clé API pour Watchmode via RapidAPI
# Obtenez votre clé sur https://rapidapi.com/gox-ai-gox-ai-default/api/watchmode
RAPIDAPI_KEY = "944e235a25msh60355e97da088e7p1eae4ajsn2bf9eb4c81bb"

# Ancienne clé Watchmode (non utilisée avec RapidAPI)
WATCHMODE_API_KEY = ""  # Remplacée par RAPIDAPI_KEY

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
        "enabled": bool(RAPIDAPI_KEY),  # Activé si clé RapidAPI disponible  
        "priority": 2,
        "timeout": 10,
        "api_key": RAPIDAPI_KEY,
        "base_url": "https://watchmode.p.rapidapi.com",
        "type": "rapidapi"
    }
}
