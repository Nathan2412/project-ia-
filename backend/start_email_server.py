"""
Script pour démarrer le serveur avec le nouveau système d'authentification par email.
"""

import os
import sys
import time

def start_server():
    """Démarre le serveur API."""
    print("🚀 Démarrage du serveur avec authentification par email")
    print("=" * 60)
    
    # Vérifier que la base de données est vide
    users_file = "data/users.json"
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            content = f.read().strip()
            if content and content != "[]":
                print("⚠️  Base de données utilisateurs existe déjà")
                print("💡 Pour un nouveau départ, supprimez data/users.json")
            else:
                print("✅ Base de données utilisateurs initialisée (vide)")
    else:
        print("✅ Nouvelle base de données utilisateurs sera créée")
    
    print("\n📋 Fonctionnalités disponibles:")
    print("   - Inscription: POST /api/register")
    print("   - Connexion: POST /api/login")
    print("   - Email obligatoire pour tous les comptes")
    print("   - Validation d'unicité d'email")
    
    print("\n🌐 Serveur disponible sur: http://localhost:5000")
    print("📧 Format d'inscription requis:")
    print("   {")
    print('     "name": "Nom Utilisateur",')
    print('     "email": "user@example.com",')
    print('     "password": "motdepasse123"')
    print("   }")
    
    print("\n▶️  Démarrage du serveur Flask...")
    
    # Démarrer le serveur
    os.system("python api.py")

if __name__ == "__main__":
    start_server()
