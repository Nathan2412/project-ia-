# WhatToWatch — Système de recommandation de films et séries

Application Vue.js + Flask qui recommande des films et séries via l'API TMDb.
**Mode LOCAL uniquement** — pas de déploiement serveur, tout tourne sur votre machine.

## Démarrage rapide (Windows)

### Option 1 : démarrer tout en un clic

```
start_all.bat
```

Ouvre deux fenêtres : backend sur `http://127.0.0.1:5000` et frontend sur `http://localhost:8080`.

### Option 2 : démarrage manuel

**Terminal 1 — Backend :**
```
start_backend.bat
```

**Terminal 2 — Frontend :**
```
start_frontend.bat
```

Puis ouvrir `http://localhost:8080` dans votre navigateur.

## Installation (première fois)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Architecture

- **Backend** : Flask + SQLAlchemy + SQLite (base locale dans `backend/data/whattowatch.db`)
- **Frontend** : Vue.js 3 + Vuex + Vue Router + Bootstrap
- **Auth** : JWT avec mots de passe hashés (Werkzeug / pbkdf2)
- **API externe** : TMDb pour les données films/séries

## Structure

```
project-ia-/
├── backend/              # API Flask
├── frontend/             # Application Vue.js
├── start_backend.bat     # Lance le backend seul
├── start_frontend.bat    # Lance le frontend seul
└── start_all.bat         # Lance les deux
```
