"""
Script de test pour le système multi-API.
Teste les fonctionnalités de recherche avec TMDb et Watchmode.
"""

import requests
import json
import sys
import os

# Ajouter le chemin du backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.multi_api_manager import api_manager
from src.recommendation_engine import search_multi_api, get_trending_multi_api

BASE_URL = "http://127.0.0.1:5000"

def test_direct_multi_api():
    """Test direct du gestionnaire multi-API."""
    print("🔍 Test direct du gestionnaire multi-API")
    print("=" * 50)
    
    # Test 1: Vérifier les fournisseurs disponibles
    print("\n1. Fournisseurs disponibles:")
    available = api_manager.get_available_providers()
    print(f"   Fournisseurs: {', '.join(available) if available else 'Aucun'}")
    
    # Test 2: Tester la connexion
    print("\n2. Test de connexion aux fournisseurs:")
    status = api_manager.test_all_providers()
    for provider, info in status.items():
        status_icon = "✅" if info["available"] else "❌"
        print(f"   {status_icon} {provider}: {'Disponible' if info['available'] else 'Non disponible'}")
    
    # Test 3: Recherche de contenu
    if available:
        print("\n3. Test de recherche (Marvel):")
        try:
            results = api_manager.search_content("Marvel", "all", combine_results=True)
            
            if "error" in results:
                print(f"   ❌ Erreur: {results['error']}")
            else:
                print(f"   ✅ {len(results.get('results', []))} résultats trouvés")
                print(f"   Fournisseurs utilisés: {', '.join(results.get('providers_used', []))}")
                
                # Afficher les 3 premiers résultats
                for i, item in enumerate(results.get('results', [])[:3], 1):
                    print(f"   📺 {i}. {item.get('title', 'N/A')} ({item.get('release_date', 'N/A')[:4]}) - {item.get('provider', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Erreur lors de la recherche: {e}")
    else:
        print("\n3. ❌ Aucun fournisseur disponible pour la recherche")

def test_api_endpoints():
    """Test des endpoints API."""
    print("\n" + "🌐 Test des endpoints API")
    print("=" * 50)
    
    try:
        # Test 1: Connexion à l'utilisateur
        print("\n1. Connexion utilisateur:")
        login_data = {"username": "Alice", "password": "password123"}
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data['token']
            user_id = data['user']['id']
            print(f"   ✅ Connecté en tant que {data['user']['name']}")
        else:
            print(f"   ❌ Échec de connexion: {response.status_code}")
            return
        
        # Test 2: Test du nouvel endpoint des fournisseurs
        print("\n2. Test de l'endpoint /api/providers:")
        response = requests.get(f"{BASE_URL}/api/providers")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Fournisseurs disponibles: {', '.join(data.get('available_providers', []))}")
            print(f"   Total fournisseurs: {data.get('total_providers', 0)}")
        else:
            print(f"   ❌ Erreur endpoint providers: {response.status_code}")
        
        # Test 3: Test des recommandations avec multi-API
        print("\n3. Test des recommandations avec multi-API:")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/recommendations/{user_id}?n=3", headers=headers)
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"   ✅ {len(recommendations)} recommandations reçues")
            
            for i, rec in enumerate(recommendations, 1):
                item = rec.get('item', {})
                provider = item.get('provider', 'N/A')
                title = item.get('title', 'N/A')
                rating = item.get('rating', 'N/A')
                print(f"   📺 {i}. {title} ({rating}/10) - Source: {provider}")
        else:
            print(f"   ❌ Erreur recommandations: {response.status_code}")
            print(f"   Réponse: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur API")
        print("Assurez-vous que le serveur Flask est en cours d'exécution")

def test_recommendation_functions():
    """Test des fonctions de recommandation."""
    print("\n" + "⚙️  Test des fonctions de recommandation")
    print("=" * 50)
    
    # Test 1: Recherche multi-API
    print("\n1. Test search_multi_api:")
    try:
        results = search_multi_api("Avengers", "movie", max_results=5)
        print(f"   ✅ {len(results)} résultats pour 'Avengers'")
        
        for i, item in enumerate(results[:3], 1):
            provider = item.get('provider', 'N/A')
            title = item.get('title', 'N/A')
            year = item.get('release_date', 'N/A')[:4] if item.get('release_date') else 'N/A'
            print(f"   📺 {i}. {title} ({year}) - {provider}")
    except Exception as e:
        print(f"   ❌ Erreur search_multi_api: {e}")
    
    # Test 2: Contenu tendance multi-API
    print("\n2. Test get_trending_multi_api:")
    try:
        results = get_trending_multi_api("movie", max_results=5)
        print(f"   ✅ {len(results)} films tendance récupérés")
        
        for i, item in enumerate(results[:3], 1):
            provider = item.get('provider', 'N/A')
            title = item.get('title', 'N/A')
            rating = item.get('vote_average', 'N/A')
            print(f"   📺 {i}. {title} ({rating}/10) - {provider}")
    except Exception as e:
        print(f"   ❌ Erreur get_trending_multi_api: {e}")

def main():
    """Fonction principale de test."""
    print("🚀 Test du système multi-API")
    print("Teste TMDb + Watchmode pour les recommandations")
    print("=" * 60)
    
    # Tests directs du gestionnaire
    test_direct_multi_api()
    
    # Tests des fonctions de recommandation
    test_recommendation_functions()
    
    # Tests des endpoints API
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("✨ Tests terminés !")
    print("\n💡 Pour configurer Watchmode:")
    print("   1. Obtenez une clé API sur https://api.watchmode.com/")
    print("   2. Ajoutez-la dans config.py: WATCHMODE_API_KEY = 'votre_cle'")
    print("   3. Redémarrez le serveur")

if __name__ == "__main__":
    main()
