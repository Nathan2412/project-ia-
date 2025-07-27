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
        print("Fichier de base de données utilisateurs non trouvé. Utilisation des utilisateurs par défaut.")
        return default_users
    
    try:
        # Vérifier que le fichier n'est pas vide
        if os.path.getsize(DATABASE_FILE) == 0:
            print("Fichier de base de données utilisateurs vide. Utilisation des utilisateurs par défaut.")
            return default_users
        
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                print("Fichier de base de données utilisateurs vide. Utilisation des utilisateurs par défaut.")
                return default_users
                
            # Revenir au début du fichier pour le charger à nouveau
            f.seek(0)
            users = json.load(f)
            
        if not users:
            print("Aucun utilisateur trouvé dans la base de données. Utilisation des utilisateurs par défaut.")
            return default_users
            
        print(f"Base de données utilisateurs chargée: {len(users)} profils trouvés.")
        return users
    except json.JSONDecodeError as e:
        print(f"Erreur de format JSON dans la base de données: {e}")
        print("Utilisation des utilisateurs par défaut.")
        return default_users
    except Exception as e:
        print(f"Erreur lors du chargement de la base de données: {e}")
        print("Utilisation des utilisateurs par défaut.")
        return default_users

def save_users(users):
    """
    Sauvegarde les utilisateurs dans le fichier de base de données.
    
    Args:
        users: Liste des utilisateurs à sauvegarder
        
    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """
    if not users:
        print("ERREUR: Tentative de sauvegarde d'une liste d'utilisateurs vide.")
        return False
        
    try:
        # Crée le répertoire parent si nécessaire
        os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
        
        # Sauvegarde dans un fichier temporaire d'abord pour éviter de corrompre le fichier original
        temp_file = DATABASE_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        
        # Vérifier que le fichier a bien été créé et qu'il contient des données
        if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
            print("ERREUR: Échec de la création du fichier temporaire.")
            return False
            
        # Remplacer le fichier original par le fichier temporaire
        if os.path.exists(DATABASE_FILE):
            os.replace(temp_file, DATABASE_FILE)
        else:
            os.rename(temp_file, DATABASE_FILE)
            
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
    try:
        # Charger les utilisateurs existants
        users = load_users()
        
        # Vérifier que la liste des utilisateurs est valide
        if not isinstance(users, list):
            print(f"ERREUR: La liste des utilisateurs n'est pas une liste valide: {type(users)}")
            # Si la liste est invalide, utiliser les utilisateurs par défaut
            from data.movies_series_database import users as default_users
            users = default_users.copy()  # Utiliser une copie pour éviter les mutations involontaires
        
        # Vérifier l'unicité de l'email
        user_email = new_user.get('email')
        if user_email:
            for existing_user in users:
                if existing_user.get('email') == user_email:
                    raise ValueError(f"Un compte avec l'email {user_email} existe déjà")
        
        # Assigner un nouvel ID unique (plus grand ID actuel + 1)
        if users:
            new_id = max(user.get('id', 0) for user in users) + 1
        else:
            new_id = 1
            
        new_user['id'] = new_id
        
        # Ajouter l'utilisateur à la liste
        users.append(new_user)
        
        # Sauvegarder la liste mise à jour
        success = save_users(users)
        if not success:
            print("ERREUR: Échec de la sauvegarde de l'utilisateur dans la base de données.")
            
        # Recharger les utilisateurs pour vérifier que tout s'est bien passé
        check_users = load_users()
        found_new_user = any(u.get('id') == new_id for u in check_users)
        if not found_new_user:
            print(f"ATTENTION: Le nouvel utilisateur ID={new_id} n'a pas été correctement sauvegardé.")
            
            # Essayer de sauvegarder à nouveau si l'utilisateur n'a pas été trouvé
            success = save_users(users)
            if success:
                print(f"Nouvelle tentative de sauvegarde effectuée.")
                
                # Vérifier à nouveau
                check_users = load_users()
                found_new_user = any(u.get('id') == new_id for u in check_users)
                if found_new_user:
                    print(f"Utilisateur ID={new_id} correctement sauvegardé après nouvelle tentative.")
                else:
                    print(f"ÉCHEC: L'utilisateur ID={new_id} n'a toujours pas été correctement sauvegardé.")
        else:
            print(f"Utilisateur ID={new_id} correctement ajouté à la base de données.")
        
        return new_user
    except Exception as e:
        print(f"Exception lors de l'ajout d'un utilisateur: {e}")
        # Ne pas perdre l'utilisateur même en cas d'erreur
        return new_user

def update_user(user):
    """
    Met à jour un utilisateur existant dans la base de données.
    
    Args:
        user: Dictionnaire contenant les informations de l'utilisateur à mettre à jour
        
    Returns:
        True si la mise à jour a réussi, False sinon
    """
    try:
        users = load_users()
        
        # Vérifier que la liste des utilisateurs est valide
        if not isinstance(users, list):
            print(f"ERREUR: La liste des utilisateurs n'est pas une liste valide: {type(users)}")
            return False
            
        # Vérifier que l'utilisateur a un ID valide
        if not user or 'id' not in user:
            print("ERREUR: Utilisateur invalide ou sans ID pour la mise à jour.")
            return False
    
        # Trouver l'index de l'utilisateur à mettre à jour
        user_index = None
        for i, u in enumerate(users):
            if u.get('id') == user.get('id'):
                user_index = i
                break
        
        if user_index is not None:
            # Remplacer l'utilisateur par la version mise à jour
            users[user_index] = user
            
            # Sauvegarder la liste mise à jour
            success = save_users(users)
            
            if success:
                print(f"Utilisateur ID={user.get('id')} mis à jour avec succès.")
                return True
            else:
                print(f"ERREUR: Échec de la sauvegarde lors de la mise à jour de l'utilisateur ID={user.get('id')}.")
                return False
        else:
            print(f"Utilisateur avec ID {user.get('id')} non trouvé pour la mise à jour.")
            return False
            
    except Exception as e:
        print(f"Exception lors de la mise à jour d'un utilisateur: {e}")
        return False

def find_user_by_email(email):
    """
    Trouve un utilisateur par son adresse email.
    
    Args:
        email: Adresse email à rechercher
        
    Returns:
        dict: Utilisateur trouvé ou None si non trouvé
    """
    try:
        users = load_users()
        for user in users:
            if user.get('email') == email:
                return user
        return None
    except Exception as e:
        print(f"Erreur lors de la recherche par email: {e}")
        return None

def find_user_by_name(name):
    """
    Trouve un utilisateur par son nom (pour compatibilité).
    
    Args:
        name: Nom à rechercher
        
    Returns:
        dict: Utilisateur trouvé ou None si non trouvé
    """
    try:
        users = load_users()
        for user in users:
            if user.get('name') == name:
                return user
        return None
    except Exception as e:
        print(f"Erreur lors de la recherche par nom: {e}")
        return None
