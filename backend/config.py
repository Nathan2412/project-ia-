"""
Configuration du système de recommandation (mode local).
Les clés API peuvent être définies soit directement ici pour le développement local,
soit via des variables d'environnement (ou un fichier .env).
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

# Clé API TMDb (The Movie Database) — obtenez la vôtre sur https://www.themoviedb.org/settings/api
TMDB_API_KEY = os.environ.get(
    'TMDB_API_KEY',
    'f584c416fc7b0c9c1591acabafc13a72'
)

# Clé API Watchmode (optionnelle) — https://api.watchmode.com/
WATCHMODE_API_KEY = os.environ.get('WATCHMODE_API_KEY', '')

# Clé RapidAPI (non utilisée par défaut)
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '')

API_PROVIDERS = {
    "tmdb": {
        "enabled": bool(TMDB_API_KEY),
        "priority": 1,
        "timeout": 10,
        "api_key": TMDB_API_KEY,
        "base_url": "https://api.themoviedb.org/3"
    },
    "watchmode": {
        "enabled": bool(WATCHMODE_API_KEY),
        "priority": 2,
        "timeout": 10,
        "api_key": WATCHMODE_API_KEY,
        "base_url": "https://api.watchmode.com/v1",
        "type": "direct"
    }
}
