# WhatToWatch - Système de Recommandation de Films et Séries

WhatToWatch est une IA qui aide les utilisateurs à choisir des films ou des séries en fonction de leurs préférences et goûts personnels, en recherchant directement en ligne via l'API TMDb.

## Structure du Projet

```
project_ia/
│
├── data/
│   └── movies_series_database.py  # Base de données des utilisateurs
│
├── src/
│   ├── recommendation_engine.py   # Moteur de recommandation en ligne
│   └── user_interface.py          # Interface utilisateur
│
├── config.py                      # Configuration du système (clé API)
└── main.py                        # Point d'entrée du programme
```

## Fonctionnalités

- Création et gestion de profils utilisateurs
- Recherche en ligne de films et séries via l'API TMDb
- Recommandations basées sur les préférences utilisateur
- Prise en compte des genres, réalisateurs et mots-clés préférés
- Information sur la disponibilité sur les services de streaming
- Filtrage des recommandations par service de streaming
- Interface en ligne de commande facile à utiliser

## Gestion de l'API TMDb

L'application interagit avec l'API TMDb pour rechercher des films/séries et savoir où ils sont disponibles en streaming.

### Architecture de gestion de l'API

- Un seul compte développeur (administrateur) possède une clé API TMDb
- Cette clé est partagée côté serveur, mais jamais visible par les utilisateurs finaux
- Chaque utilisateur final peut faire une recherche personnalisée (par titre, préférence, etc.)
- Toutes les requêtes passent par le même backend qui utilise la clé API de l'administrateur

Cette architecture centralisée permet de :
- Sécuriser la clé API en évitant de l'exposer aux utilisateurs
- Simplifier l'expérience utilisateur (pas besoin de créer un compte TMDb)
- Mutualiser les quotas d'API et surveiller la consommation globale
- Éviter aux utilisateurs de gérer leurs propres clés API

## Installation des dépendances

```
pip install requests keyboard
```

## Comment utiliser

1. Exécutez le programme en lançant `main.py` :

```
python main.py
```

2. Le système utilise automatiquement une clé API administrateur préinstallée.

3. Suivez les instructions à l'écran pour :
   - Créer un nouveau profil utilisateur
   - Vous connecter avec un profil existant
   - Obtenir des recommandations de films et séries en ligne
   - Filtrer les recommandations par service de streaming
   - Mettre à jour vos préférences

4. Vous pouvez arrêter le programme à tout moment en :
   - Appuyant sur la touche Échap
   - Sélectionnant l'option "0. Quitter immédiatement" dans n'importe quel menu

## Fonctionnement de la Recherche en Ligne

Le système utilise l'API TMDb pour rechercher en temps réel des films et séries qui correspondent à vos préférences. Cette méthode fournit :
- Des résultats récents et variés
- Des informations à jour sur les notes et la popularité
- Des images d'affiches de films/séries
- Des informations sur la disponibilité en streaming

## Algorithme de Recommandation

Le système calcule des scores de similarité entre les préférences d'un utilisateur et les caractéristiques des films/séries. Les facteurs pris en compte sont :

- Correspondance des genres aimés/non aimés
- Réalisateurs/créateurs préférés
- Mots-clés d'intérêt
- Notes minimales exigées
- Popularité actuelle

## Services de Streaming

Le système fournit des informations sur la disponibilité des contenus sur les services suivants :
- Netflix
- Disney+
- Amazon Prime Video
- HBO Max

Ces informations proviennent de l'API TMDb et sont basées sur les données de disponibilité à jour.

## Extension Future

Pour améliorer ce système, vous pourriez :

1. Ajouter une interface graphique
2. Implémenter une base de données pour stocker l'historique des utilisateurs
3. Améliorer l'algorithme de recommandation avec des techniques de machine learning
4. Ajouter un système de notation par l'utilisateur
5. Implémenter un filtrage collaboratif en plus du filtrage basé sur le contenu
6. Intégrer d'autres APIs comme JustWatch pour des informations plus précises sur la disponibilité en streaming
