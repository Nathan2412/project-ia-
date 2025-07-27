"""
Script de migration pour ajouter l'authentification aux utilisateurs existants.
Ce script ajoute les champs d'authentification aux utilisateurs qui n'en ont pas.
"""

import json
import os
from src.auth import hash_password
from datetime import datetime

def migrate_users_to_auth():
    """
    Migre les utilisateurs existants pour ajouter l'authentification.
    Mot de passe par défaut: "password123" (à changer après la première connexion)
    """
    database_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.json")
    
    if not os.path.exists(database_file):
        print("Fichier de base de données non trouvé.")
        return
    
    # Charger les utilisateurs existants
    with open(database_file, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    # Mot de passe par défaut pour les utilisateurs existants
    default_password = "password123"
    
    updated_count = 0
    
    for user in users:
        # Vérifier si l'utilisateur a déjà des informations d'authentification
        if 'auth' not in user:
            print(f"Migration de l'utilisateur: {user['name']}")
            
            # Hash du mot de passe par défaut
            password_hash, salt = hash_password(default_password)
            
            # Ajouter les informations d'authentification
            user['auth'] = {
                'password_hash': password_hash,
                'salt': salt,
                'created_at': datetime.utcnow().isoformat(),
                'migrated': True  # Marquer comme migré
            }
            
            updated_count += 1
        else:
            print(f"L'utilisateur {user['name']} a déjà l'authentification configurée.")
    
    if updated_count > 0:
        # Sauvegarder les modifications
        with open(database_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Migration terminée!")
        print(f"📊 {updated_count} utilisateur(s) migré(s).")
        print(f"🔑 Mot de passe par défaut: '{default_password}'")
        print("⚠️  Les utilisateurs doivent changer leur mot de passe après la première connexion!")
    else:
        print("✅ Aucune migration nécessaire. Tous les utilisateurs ont déjà l'authentification configurée.")

if __name__ == "__main__":
    print("🔄 Début de la migration des utilisateurs...")
    migrate_users_to_auth()
    print("✨ Migration terminée!")
