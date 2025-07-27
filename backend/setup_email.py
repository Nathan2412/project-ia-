"""
Script de configuration pour le service d'email.
Aide à configurer l'envoi d'emails pour les notifications utilisateur.
"""

import os
import sys

def setup_email_configuration():
    """
    Guide l'utilisateur dans la configuration du service d'email.
    """
    print("📧 Configuration du service d'email WhatToWatch")
    print("=" * 50)
    
    print("\n🔧 Instructions de configuration:")
    print("\n1. Gmail (Recommandé)")
    print("   - Activez l'authentification à 2 facteurs sur votre compte Gmail")
    print("   - Générez un 'Mot de passe d'application' spécifique")
    print("   - Utilisez ce mot de passe d'application (pas votre mot de passe Gmail)")
    
    print("\n2. Autres fournisseurs d'email")
    print("   - Vérifiez les paramètres SMTP de votre fournisseur")
    print("   - Modifiez smtp_server et smtp_port dans email_service.py")
    
    print("\n🔑 Variables d'environnement à définir:")
    print("\nPour Windows (PowerShell):")
    print("$env:SENDER_EMAIL='votre-email@gmail.com'")
    print("$env:SENDER_PASSWORD='votre-mot-de-passe-app'")
    
    print("\nPour Windows (Command Prompt):")
    print("set SENDER_EMAIL=votre-email@gmail.com")
    print("set SENDER_PASSWORD=votre-mot-de-passe-app")
    
    print("\nPour Linux/Mac:")
    print("export SENDER_EMAIL='votre-email@gmail.com'")
    print("export SENDER_PASSWORD='votre-mot-de-passe-app'")
    
    print("\n💡 Test de la configuration:")
    print("python test_email_config.py")
    
    # Vérifier la configuration actuelle
    print("\n🔍 Configuration actuelle:")
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    if sender_email:
        print(f"✅ SENDER_EMAIL configuré: {sender_email}")
    else:
        print("❌ SENDER_EMAIL non configuré")
    
    if sender_password:
        print("✅ SENDER_PASSWORD configuré")
    else:
        print("❌ SENDER_PASSWORD non configuré")
    
    if sender_email and sender_password:
        print("\n🎉 Configuration complète ! Vous pouvez maintenant envoyer des emails.")
        
        # Test de configuration
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from src.email_service import email_service
            
            print("\n🧪 Test de connexion SMTP...")
            if email_service.test_email_configuration():
                print("✅ Service d'email prêt !")
            else:
                print("❌ Problème de configuration détecté")
        except Exception as e:
            print(f"❌ Erreur lors du test: {str(e)}")
    else:
        print("\n⚠️  Configuration incomplète. Définissez les variables d'environnement.")

def create_env_file():
    """
    Crée un fichier .env d'exemple.
    """
    env_content = """# Configuration email pour WhatToWatch
# Dupliquez ce fichier en .env et remplissez vos vraies valeurs

SENDER_EMAIL=votre-email@gmail.com
SENDER_PASSWORD=votre-mot-de-passe-app

# Instructions:
# 1. Activez l'authentification à 2 facteurs sur Gmail
# 2. Générez un mot de passe d'application
# 3. Utilisez ce mot de passe d'application ici
# 4. Pour charger ce fichier, utilisez: python-dotenv
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Fichier .env.example créé")
    print("💡 Copiez-le en .env et remplissez vos vraies valeurs")

if __name__ == "__main__":
    setup_email_configuration()
    
    print("\n" + "=" * 50)
    response = input("Voulez-vous créer un fichier .env d'exemple ? (o/n): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        create_env_file()
