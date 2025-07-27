# Système d'Authentification - Documentation

## Vue d'ensemble

Le système d'authentification a été ajouté pour sécuriser l'API de recommandation. Chaque utilisateur doit maintenant se connecter avec un nom d'utilisateur et un mot de passe pour accéder à ses données.

## Fonctionnalités

- ✅ **Inscription** (`/api/register`) - Créer un nouveau compte
- ✅ **Connexion** (`/api/login`) - Se connecter avec nom d'utilisateur/mot de passe
- ✅ **Tokens JWT** - Authentification sécurisée avec tokens
- ✅ **Protection des routes** - Seuls les utilisateurs connectés peuvent accéder à leurs données
- ✅ **Changement de mot de passe** (`/api/change-password`)
- ✅ **Vérification de token** (`/api/verify-token`)

## Installation et Configuration

### 1. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Migrer les utilisateurs existants

```bash
python migrate_users.py
```

Cette commande ajoute l'authentification aux utilisateurs existants avec le mot de passe par défaut : `password123`

### 3. Démarrer le serveur

```bash
python api.py
```

## Endpoints API

### Routes publiques (pas d'authentification requise)

#### `POST /api/register`
Créer un nouveau compte utilisateur.

**Body JSON :**
```json
{
    "username": "nom_utilisateur",
    "password": "mot_de_passe",
    "preferences": {
        "genres_likes": ["Action", "Science-Fiction"],
        "genres_dislikes": ["Horreur"],
        "rating_min": 7.0,
        "streaming_services": ["netflix"]
    }
}
```

**Réponse :**
```json
{
    "message": "Inscription réussie",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "name": "nom_utilisateur",
        "preferences": {...}
    }
}
```

#### `POST /api/login`
Se connecter avec un compte existant.

**Body JSON :**
```json
{
    "username": "nom_utilisateur",
    "password": "mot_de_passe"
}
```

**Réponse :**
```json
{
    "message": "Connexion réussie",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "name": "nom_utilisateur",
        "preferences": {...}
    }
}
```

#### `GET /api/genres`
Récupérer la liste des genres disponibles.

#### `GET /api/services`
Récupérer la liste des services de streaming.

### Routes protégées (authentification requise)

**⚠️ Important :** Toutes les routes ci-dessous nécessitent un token d'authentification dans l'en-tête :
```
Authorization: Bearer <token>
```

#### `GET /api/verify-token`
Vérifier la validité du token actuel.

#### `POST /api/change-password`
Changer le mot de passe de l'utilisateur connecté.

**Body JSON :**
```json
{
    "current_password": "ancien_mot_de_passe",
    "new_password": "nouveau_mot_de_passe"
}
```

#### `GET /api/users/<user_id>`
Récupérer les informations d'un utilisateur (seulement son propre compte).

#### `PUT /api/users/<user_id>`
Mettre à jour les préférences d'un utilisateur (seulement son propre compte).

#### `GET /api/recommendations/<user_id>`
Récupérer les recommandations pour un utilisateur (seulement son propre compte).

#### `POST /api/history/<user_id>/<item_id>`
Ajouter un élément à l'historique d'un utilisateur (seulement son propre compte).

## Sécurité

### Protection des comptes
- ✅ Les utilisateurs ne peuvent accéder qu'à leur propre compte
- ✅ Les mots de passe sont hashés avec SHA-256 + salt
- ✅ Les tokens JWT expirent après 24 heures
- ✅ Validation des données d'entrée

### Règles de mot de passe
- Minimum 6 caractères
- Recommandé : combinaison de lettres, chiffres et caractères spéciaux

## Utilisation côté Frontend

### 1. Inscription/Connexion
```javascript
// Inscription
const registerResponse = await fetch('/api/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'monnom',
        password: 'monmotdepasse',
        preferences: {...}
    })
});

const { token, user } = await registerResponse.json();

// Stocker le token
localStorage.setItem('auth_token', token);
```

### 2. Appels API avec authentification
```javascript
// Récupérer le token
const token = localStorage.getItem('auth_token');

// Faire un appel API
const response = await fetch(`/api/users/${userId}`, {
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
});
```

### 3. Vérification du token
```javascript
const verifyToken = async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return false;
    
    try {
        const response = await fetch('/api/verify-token', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        return response.ok;
    } catch {
        return false;
    }
};
```

## Migration des utilisateurs existants

Les utilisateurs existants (Alice, Bob, Nathan) ont été migrés avec le mot de passe par défaut : `password123`

**Pour se connecter avec un utilisateur existant :**
```json
{
    "username": "Alice",
    "password": "password123"
}
```

**⚠️ Important :** Changez immédiatement le mot de passe après la première connexion !

## Codes d'erreur

- `400` - Données manquantes ou invalides
- `401` - Token manquant, invalide ou expiré
- `403` - Accès interdit à ce compte
- `404` - Utilisateur non trouvé
- `409` - Utilisateur déjà existant (inscription)
- `500` - Erreur serveur

## Développement

### Structure des fichiers
```
backend/
├── src/
│   ├── auth.py           # Module d'authentification
│   ├── auth_routes.py    # Routes d'authentification
│   └── middleware.py     # Middleware de sécurité
├── migrate_users.py      # Script de migration
└── api.py               # API principale (modifiée)
```

### Configuration
Pour changer la clé secrète JWT (production), modifiez `JWT_SECRET_KEY` dans `src/auth.py`.

### Tests
Vous pouvez tester l'API avec curl ou Postman :

```bash
# Connexion
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "Alice", "password": "password123"}'

# Utiliser le token retourné
curl -X GET http://localhost:5000/api/users/1 \
  -H "Authorization: Bearer <votre_token>"
```
