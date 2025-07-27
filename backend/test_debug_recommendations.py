"""
Test avec affichage complet des données de recommandations.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_recommendations_debug():
    """Test avec debug complet."""
    print("🔍 Test debug des recommandations")
    print("=" * 40)
    
    # Connexion
    login_data = {"username": "Alice", "password": "password123"}
    response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    data = response.json()
    token = data['token']
    user_id = data['user']['id']
    
    # Test recommandations
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/recommendations/{user_id}?n=2", headers=headers)
    
    if response.status_code == 200:
        recommendations = response.json()
        print(f"✅ Données reçues (format JSON brut):")
        print(json.dumps(recommendations, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_recommendations_debug()
