"""
Script de test pour vérifier que l'API répond correctement.
Ce script teste les différents endpoints de l'API et affiche les résultats.
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:5000/api"

def print_response(response, endpoint):
    """Affiche la réponse d'une requête API de manière formatée."""
    print(f"\n=== Test de l'endpoint {endpoint} ===")
    print(f"Status code: {response.status_code}")
    try:
        data = response.json()
        print(f"Réponse (formatée):")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "..." if len(json.dumps(data)) > 500 else json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Impossible de parser la réponse en JSON: {e}")
        print(f"Contenu brut: {response.text[:500]}")

def test_api_status():
    """Teste l'endpoint de statut de l'API."""
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        print_response(response, "/status")
    except Exception as e:
        print(f"Erreur lors du test de l'endpoint /status: {e}")

def test_get_users():
    """Teste l'endpoint pour récupérer les utilisateurs."""
    try:
        response = requests.get(f"{API_BASE_URL}/users")
        print_response(response, "/users")
    except Exception as e:
        print(f"Erreur lors du test de l'endpoint /users: {e}")

def test_get_genres():
    """Teste l'endpoint pour récupérer les genres."""
    try:
        response = requests.get(f"{API_BASE_URL}/genres")
        print_response(response, "/genres")
    except Exception as e:
        print(f"Erreur lors du test de l'endpoint /genres: {e}")

def test_get_services():
    """Teste l'endpoint pour récupérer les services de streaming."""
    try:
        response = requests.get(f"{API_BASE_URL}/services")
        print_response(response, "/services")
    except Exception as e:
        print(f"Erreur lors du test de l'endpoint /services: {e}")

def test_get_recommendations():
    """Teste l'endpoint pour récupérer des recommandations pour un utilisateur."""
    try:
        user_id = 1  # Alice
        response = requests.get(f"{API_BASE_URL}/recommendations/{user_id}?n=3")
        print_response(response, f"/recommendations/{user_id}")
    except Exception as e:
        print(f"Erreur lors du test de l'endpoint /recommendations: {e}")

if __name__ == "__main__":
    print("=== Test de l'API de recommandation ===")
    print(f"URL de base: {API_BASE_URL}")
    
    test_api_status()
    test_get_users()
    test_get_genres()
    test_get_services()
    test_get_recommendations()
    
    print("\n=== Tests terminés ===")
