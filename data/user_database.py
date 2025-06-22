"""
Module de gestion de la base de données utilisateurs.
Permet de sauvegarder et charger les profils utilisateurs dans un fichier.
"""

import os
import json
import sys

# Chemin du fichier de base de données utilisateurs
DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")

def load_users():
    """
    Charge les utilisateurs depuis le fichier de base de données.
    Si le fichier n'existe pas, retourne la liste d'utilisateurs par défaut.
    """
    from data.movies_series_database import users as default_users
    
    if not os.path.exists(DATABASE_FILE):
        return default_users
    
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        print(f"Base de données utilisateurs chargée: {len(users)} profils trouvés.")
        return users
    except Exception as e:
        print(f"Erreur lors du chargement de la base de données: {e}")
        print("Utilisation des utilisateurs par défaut.")
        return default_users

def save_users(users):
    """
    Sauvegarde les utilisateurs dans le fichier de base de données.
    
    Args:
        users: Liste des utilisateurs à sauvegarder
    """
    try:
        # Crée le répertoire parent si nécessaire
        os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
        
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        print(f"Base de données utilisateurs sauvegardée: {len(users)} profils.")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la base de données: {e}")
        return False

def add_user(new_user):
    """
    Ajoute un nouveau utilisateur à la base de données.
    
    Args:
        new_user: Dictionnaire contenant les informations du nouvel utilisateur
        
    Returns:
        L'utilisateur ajouté avec un ID unique
    """
    users = load_users()
    
    # Assigner un nouvel ID unique (plus grand ID actuel + 1)
    if users:
        new_id = max(user['id'] for user in users) + 1
    else:
        new_id = 1
        
    new_user['id'] = new_id
    
    # Ajouter l'utilisateur à la liste
    users.append(new_user)
    
    # Sauvegarder la liste mise à jour
    save_users(users)
    
    return new_user

def update_user(user):
    """
    Met à jour un utilisateur existant dans la base de données.
    
    Args:
        user: Dictionnaire contenant les informations de l'utilisateur à mettre à jour
        
    Returns:
        True si la mise à jour a réussi, False sinon
    """
    users = load_users()
    
    # Trouver l'index de l'utilisateur à mettre à jour
    user_index = None
    for i, u in enumerate(users):
        if u['id'] == user['id']:
            user_index = i
            break
    
    if user_index is not None:
        # Remplacer l'utilisateur par la version mise à jour
        users[user_index] = user
        return save_users(users)
    else:
        print(f"Utilisateur avec ID {user['id']} non trouvé.")
        return False
