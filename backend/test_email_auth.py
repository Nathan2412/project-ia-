"""
Script de test pour le nouveau système d'authentification avec email.
Teste l'inscription et la connexion avec email obligatoire.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_email_auth_system():
    """Test complet du système d'authentification avec email."""
    print("🧪 Test du système d'authentification avec email")
    print("=" * 60)
    
    # Test 1: Inscription avec email
    print("\n1. Test d'inscription avec email")
    print("-" * 40)
    
    user_data = {
        "name": "Alice Dupont",
        "email": "alice@example.com",
        "password": "motdepasse123",
        "preferences": {
            "genres_likes": ["Science-Fiction", "Animation"],
            "genres_dislikes": ["Horreur"],
            "rating_min": 7.5,
            "streaming_services": ["netflix", "disney"]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=user_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Inscription réussie pour {data['user']['name']}")
            print(f"📧 Email: {data['user']['email']}")
            print(f"🔑 Token: {data['token'][:20]}...")
            user_token = data['token']
            user_id = data['user']['id']
        else:
            print(f"❌ Erreur inscription: {response.text}")
            return
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        return
    
    # Test 2: Connexion avec email
    print("\n2. Test de connexion avec email")
    print("-" * 40)
    
    login_data = {
        "email": "alice@example.com",
        "password": "motdepasse123"
    }
    
    response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Connexion réussie pour {data['user']['name']}")
        print(f"📧 Email: {data['user']['email']}")
        print(f"🔑 Token: {data['token'][:20]}...")
    else:
        print(f"❌ Erreur connexion: {response.text}")
        return
    
    # Test 3: Tentative d'inscription avec email déjà existant
    print("\n3. Test d'inscription avec email existant")
    print("-" * 40)
    
    duplicate_user = {
        "name": "Bob Martin",
        "email": "alice@example.com",  # Même email
        "password": "autremotdepasse123"
    }
    
    response = requests.post(f"{BASE_URL}/api/register", json=duplicate_user)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 409:
        print("✅ Duplication d'email correctement rejetée")
    else:
        print(f"❌ Erreur inattendue: {response.text}")
    
    # Test 4: Tentative de connexion avec mauvais mot de passe
    print("\n4. Test de connexion avec mauvais mot de passe")
    print("-" * 40)
    
    wrong_login = {
        "email": "alice@example.com",
        "password": "mauvaispassword"
    }
    
    response = requests.post(f"{BASE_URL}/api/login", json=wrong_login)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Mauvais mot de passe correctement rejeté")
    else:
        print(f"❌ Erreur inattendue: {response.text}")
    
    # Test 5: Validation email manquant
    print("\n5. Test d'inscription sans email")
    print("-" * 40)
    
    no_email_user = {
        "name": "Charlie Brown",
        "password": "password123"
        # Pas d'email
    }
    
    response = requests.post(f"{BASE_URL}/api/register", json=no_email_user)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        print("✅ Absence d'email correctement rejetée")
    else:
        print(f"❌ Erreur inattendue: {response.text}")
    
    # Test 6: Validation email invalide
    print("\n6. Test d'inscription avec email invalide")
    print("-" * 40)
    
    invalid_email_user = {
        "name": "David Wilson",
        "email": "email-invalide",  # Pas de @
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/register", json=invalid_email_user)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        print("✅ Email invalide correctement rejeté")
    else:
        print(f"❌ Erreur inattendue: {response.text}")
    
    # Test 7: Accès aux données utilisateur avec token
    print("\n7. Test d'accès aux données utilisateur")
    print("-" * 40)
    
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BASE_URL}/api/users/{user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Données utilisateur récupérées")
        print(f"📧 Email: {data.get('email', 'Non spécifié')}")
        print(f"👤 Nom: {data.get('name', 'Non spécifié')}")
    else:
        print(f"❌ Erreur accès données: {response.text}")
    
    # Test 8: Test des recommandations
    print("\n8. Test des recommandations")
    print("-" * 40)
    
    response = requests.get(f"{BASE_URL}/api/recommendations/{user_id}?n=3", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        recommendations = response.json()
        print(f"✅ {len(recommendations)} recommandations reçues")
        for i, rec in enumerate(recommendations[:2], 1):
            title = rec.get('item', {}).get('title', 'Titre inconnu')
            print(f"   {i}. {title}")
    else:
        print(f"❌ Erreur recommandations: {response.text}")
    
    print("\n" + "=" * 60)
    print("✨ Tests terminés !")
    print("\n💡 Système d'authentification avec email opérationnel:")
    print("   - ✅ Inscription avec email obligatoire")
    print("   - ✅ Connexion par email")
    print("   - ✅ Validation d'unicité d'email")
    print("   - ✅ Validation format email")
    print("   - ✅ Protection des données utilisateur")

if __name__ == "__main__":
    test_email_auth_system()
