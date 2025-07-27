"""
Script de test pour l'API d'authentification.
Ce script teste toutes les fonctionnalités d'authentification.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_auth_api():
    """
    Test complet de l'API d'authentification.
    """
    print("🧪 Test de l'API d'authentification")
    print("=" * 50)
    
    # Test 1: Connexion avec utilisateur existant
    print("\n1. Test de connexion avec utilisateur existant")
    login_data = {
        "username": "Alice",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Connexion réussie !")
            print(f"Utilisateur: {data['user']['name']}")
            print(f"ID: {data['user']['id']}")
            
            # Sauvegarder le token pour les tests suivants
            token = data['token']
            user_id = data['user']['id']
        else:
            print("❌ Échec de la connexion")
            print(response.text)
            return
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur")
        print("Assurez-vous que le serveur Flask est en cours d'exécution")
        return
    
    # Test 2: Vérification du token
    print("\n2. Test de vérification du token")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/verify-token", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Token valide !")
        data = response.json()
        print(f"Utilisateur vérifié: {data['user']['name']}")
    else:
        print("❌ Token invalide")
        print(response.text)
    
    # Test 3: Accès aux données utilisateur
    print(f"\n3. Test d'accès aux données utilisateur (ID: {user_id})")
    
    response = requests.get(f"{BASE_URL}/api/users/{user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Accès aux données utilisateur réussi !")
        data = response.json()
        print(f"Nom: {data['name']}")
        print(f"Genres préférés: {data['preferences']['genres_likes']}")
    else:
        print("❌ Échec d'accès aux données utilisateur")
        print(response.text)
    
    # Test 4: Tentative d'accès aux données d'un autre utilisateur
    print(f"\n4. Test d'accès non autorisé (tentative d'accès à l'utilisateur ID: 2)")
    
    response = requests.get(f"{BASE_URL}/api/users/2", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 403:
        print("✅ Accès correctement refusé !")
        data = response.json()
        print(f"Message: {data['error']}")
    else:
        print("❌ Problème de sécurité: accès non autorisé permis")
        print(response.text)
    
    # Test 5: Recommandations
    print(f"\n5. Test de récupération des recommandations")
    
    response = requests.get(f"{BASE_URL}/api/recommendations/{user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Recommandations récupérées !")
        data = response.json()
        print(f"Nombre de recommandations: {len(data)}")
        if data:
            print(f"Première recommandation: {data[0].get('title', 'N/A')}")
    else:
        print("❌ Échec de récupération des recommandations")
        print(response.text)
    
    # Test 6: Changement de mot de passe
    print("\n6. Test de changement de mot de passe")
    change_password_data = {
        "current_password": "password123",
        "new_password": "nouveaumotdepasse123"
    }
    
    response = requests.post(f"{BASE_URL}/api/change-password", 
                           json=change_password_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Mot de passe changé avec succès !")
        
        # Test de connexion avec le nouveau mot de passe
        print("\n7. Test de connexion avec le nouveau mot de passe")
        new_login_data = {
            "username": "Alice",
            "password": "nouveaumotdepasse123"
        }
        
        response = requests.post(f"{BASE_URL}/api/login", json=new_login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Connexion avec nouveau mot de passe réussie !")
            
            # Remettre l'ancien mot de passe pour ne pas casser les autres tests
            data = response.json()
            new_token = data['token']
            new_headers = {"Authorization": f"Bearer {new_token}"}
            
            restore_password_data = {
                "current_password": "nouveaumotdepasse123",
                "new_password": "password123"
            }
            
            requests.post(f"{BASE_URL}/api/change-password", 
                         json=restore_password_data, headers=new_headers)
            print("🔄 Mot de passe restauré à la valeur par défaut")
        else:
            print("❌ Échec de connexion avec le nouveau mot de passe")
    else:
        print("❌ Échec du changement de mot de passe")
        print(response.text)
    
    # Test 7: Test avec token invalide
    print("\n8. Test avec token invalide")
    invalid_headers = {"Authorization": "Bearer token_invalide"}
    
    response = requests.get(f"{BASE_URL}/api/verify-token", headers=invalid_headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Token invalide correctement rejeté !")
        data = response.json()
        print(f"Message: {data['error']}")
    else:
        print("❌ Problème: token invalide accepté")
    
    # Test 8: Test sans token
    print("\n9. Test d'accès sans token")
    
    response = requests.get(f"{BASE_URL}/api/users/1")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Accès sans token correctement refusé !")
        data = response.json()
        print(f"Message: {data['error']}")
    else:
        print("❌ Problème: accès sans token permis")
    
    # Test 9: Test d'inscription d'un nouvel utilisateur
    print("\n10. Test d'inscription d'un nouvel utilisateur")
    register_data = {
        "username": "testuser",
        "password": "testpassword123",
        "preferences": {
            "genres_likes": ["Action", "Comedy"],
            "rating_min": 7.5
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/register", json=register_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Inscription réussie !")
        data = response.json()
        print(f"Nouvel utilisateur: {data['user']['name']}")
        print(f"ID: {data['user']['id']}")
    elif response.status_code == 409:
        print("ℹ️  Utilisateur déjà existant (normal si déjà testé)")
    else:
        print("❌ Échec de l'inscription")
        print(response.text)
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés !")

if __name__ == "__main__":
    test_auth_api()
