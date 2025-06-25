"""
Script d'urgence pour réinitialiser la base de données utilisateurs.
Ce script va restaurer les utilisateurs par défaut et les sauvegarder dans le fichier users.json.
"""

import os
import json
import sys

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.movies_series_database import users as default_users
from data.user_database import DATABASE_FILE, save_users

def reset_database():
    """Réinitialise la base de données utilisateurs avec les valeurs par défaut."""
    try:
        # S'assurer que le répertoire existe
        os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
        
        # Afficher les utilisateurs par défaut
        print(f"Restauration de {len(default_users)} utilisateurs par défaut:")
        for user in default_users:
            print(f" - ID: {user['id']}, Nom: {user['name']}")
        
        # Sauvegarder directement les utilisateurs par défaut
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=4)
        
        print(f"\nFichier de base de données restauré: {DATABASE_FILE}")
        print(f"{len(default_users)} utilisateurs restaurés avec succès.")
        
        # Vérifier que le fichier a bien été créé
        if os.path.exists(DATABASE_FILE):
            print(f"Vérification du fichier: OK - {os.path.getsize(DATABASE_FILE)} octets")
            # Lire le fichier pour vérifier qu'il est valide
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                restored_users = json.load(f)
            print(f"Vérification du contenu: OK - {len(restored_users)} utilisateurs lus")
        else:
            print("ERREUR: Le fichier n'a pas été créé!")
            
        return True
    except Exception as e:
        print(f"ERREUR lors de la réinitialisation de la base de données: {e}")
        return False

if __name__ == "__main__":
    print("=== RESTAURATION D'URGENCE DE LA BASE DE DONNÉES UTILISATEURS ===")
    
    # Déterminer si le fichier existe déjà
    if os.path.exists(DATABASE_FILE):
        choice = input(f"Le fichier {DATABASE_FILE} existe déjà. Voulez-vous le remplacer? (o/n): ")
        if choice.lower() not in ['o', 'oui', 'y', 'yes']:
            print("Opération annulée.")
            sys.exit(0)
    
    # Réinitialiser la base de données
    success = reset_database()
    
    if success:
        print("\nLa base de données a été restaurée avec succès.")
        print("Vous pouvez maintenant redémarrer votre application.")
    else:
        print("\nLa restauration a échoué. Veuillez vérifier les messages d'erreur ci-dessus.")
