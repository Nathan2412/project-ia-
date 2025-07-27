"""
Test simple pour les recommandations uniquement.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_recommendations_only():
    """Test uniquement la fonctionnalité de recommandations."""
    print("🧪 Test des recommandations uniquement")
    print("=" * 40)
    
    # 1. Se connecter pour obtenir un token
    print("1. Connexion...")
    login_data = {
        "username": "Alice",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data['token']
            user_id = data['user']['id']
            print(f"✅ Connecté en tant que {data['user']['name']} (ID: {user_id})")
        else:
            print("❌ Échec de la connexion")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Serveur non accessible")
        return
    
    # 2. Test des recommandations
    print("\n2. Test des recommandations...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/recommendations/{user_id}?n=3", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ {len(recommendations)} recommandations reçues !")
            
            for i, rec in enumerate(recommendations, 1):
                item = rec.get('item', {})
                print(f"\n📺 Recommandation {i}:")
                print(f"   Titre: {item.get('title', 'N/A')}")
                print(f"   Note: {item.get('rating', 'N/A')}/10")
                print(f"   Genre: {', '.join(item.get('genre', []))}")
                print(f"   Type: {rec.get('type', 'N/A')}")
                print(f"   Score: {rec.get('score', 'N/A'):.2f}")
                if item.get('plot'):
                    print(f"   Résumé: {item['plot'][:100]}...")
                if rec.get('streaming_services'):
                    services = list(set(rec['streaming_services']))  # Enlever les doublons
                    print(f"   Disponible sur: {', '.join(services)}")
        else:
            print("❌ Erreur lors de la récupération des recommandations")
            print(f"Réponse: {response.text}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 40)
    print("Test terminé !")

if __name__ == "__main__":
    test_recommendations_only()
