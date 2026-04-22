# Backend WhatToWatch — Mode LOCAL

API Flask pour le système de recommandation de films et séries.
**Configuration pour développement local uniquement** (SQLite, pas de déploiement serveur).

## Installation

```bash
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
# ou : source venv/bin/activate sur Linux/Mac

pip install -r requirements.txt
```

## Démarrage

```bash
python api.py
```

L'API démarre sur `http://127.0.0.1:5000`.
La base SQLite `data/whattowatch.db` est créée automatiquement au premier démarrage.

## Variables d'environnement (optionnel)

Créer un fichier `.env` à la racine de `backend/` :

```
JWT_SECRET_KEY=ma-cle-secrete-locale
TMDB_API_KEY=votre-cle-tmdb
WATCHMODE_API_KEY=votre-cle-watchmode
```

## Endpoints principaux

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| GET | `/api/ping` | Non | Test que l'API tourne |
| POST | `/api/register` | Non | Inscription |
| POST | `/api/login` | Non | Connexion (retourne un JWT) |
| GET | `/api/verify-token` | Oui | Vérifie un JWT |
| GET | `/api/genres` | Non | Liste des genres |
| GET | `/api/services` | Non | Services de streaming |
| GET | `/api/users/<id>` | Oui | Infos utilisateur |
| PUT | `/api/users/<id>` | Oui | Mettre à jour ses préférences |
| GET | `/api/recommendations/<id>` | Oui | Obtenir des recommandations |
| POST | `/api/users/<id>/history` | Oui | Ajouter à l'historique |
| POST | `/api/change-password` | Oui | Changer son mot de passe |

## Authentification

L'API utilise JWT Bearer tokens. Après `/api/login` ou `/api/register`, ajouter à chaque requête authentifiée :

```
Authorization: Bearer <votre-token>
```

## Architecture

```
backend/
├── api.py                      # Routes Flask principales
├── config.py                   # Config clés API
├── models.py                   # Modèles SQLAlchemy (User)
├── requirements.txt
├── data/
│   ├── whattowatch.db          # Base SQLite (créée auto)
│   └── movies_series_database.py
└── src/
    ├── auth.py                 # Hash password + JWT
    ├── middleware.py           # Middleware d'auth Flask
    ├── recommendation_engine_v2.py
    ├── recommendation_scoring.py
    ├── recommendation_utils.py
    └── api_providers/
        ├── tmdb_provider.py
        └── watchmode_provider.py
```
