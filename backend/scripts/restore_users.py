"""
Script d'urgence pour restaurer les utilisateurs par défaut.
Ce script réinitialise le fichier users.json avec les utilisateurs définis dans movies_series_database.py.
"""

import os
import json
import sys

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.movies_series_database import users as default_users

# Chemin du fichier de base de données utilisateurs
DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.json")

def restore_default_users():
    """
    Restaure les utilisateurs par défaut dans le fichier de base de données.
    """
    print(f"\n=== RESTAURATION DES UTILISATEURS PAR DÉFAUT ===")
    
    try:
        # Sauvegarder l'ancien fichier si il existe
        if os.path.exists(DATABASE_FILE):
            backup_file = DATABASE_FILE + '.backup'
            try:
                os.replace(DATABASE_FILE, backup_file)
                print(f"L'ancien fichier a été sauvegardé sous: {backup_file}")
            except Exception as e:
                print(f"Impossible de sauvegarder l'ancien fichier: {e}")
        
        # Créer le répertoire parent si nécessaire
        os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
        
        # Écrire les utilisateurs par défaut dans le fichier
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Les utilisateurs par défaut ({len(default_users)}) ont été restaurés avec succès!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la restauration des utilisateurs par défaut: {e}")
        return False

if __name__ == "__main__":
    restore_default_users()
    input("\nAppuyez sur Entrée pour quitter...")
