"""
Script de test pour le moteur de recommandation.
"""

import sys
import os

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommendation_engine import get_recommendations, create_user_profile

def test_recommendation_engine():
    """
    Teste le moteur de recommandation avec un nouveau profil utilisateur.
    """
    print("=== TEST DU MOTEUR DE RECOMMANDATION ===\n")
    
    # Créer un nouveau profil de test
    test_user = create_user_profile(
        name="Test User",
        genres_likes=["Action", "Science-Fiction", "Thriller"],
        genres_dislikes=["Horreur"],
        directors_likes=["Christopher Nolan"],
        keywords_likes=["space", "rêve", "aventure"],
        mood_preferences=["intense", "épique"],
        rating_min=8.0
    )
    
    print(f"Profil de test créé: {test_user['name']}\n")
    print(f"Préférences: {test_user['preferences']}\n")
    
    # Obtenir des recommandations
    print("Obtention des recommandations...")
    recommendations = get_recommendations(test_user['id'], n=10)
    
    # Afficher les recommandations
    print("\nRECOMMANDATIONS:\n")
    for i, rec in enumerate(recommendations, 1):
        item = rec['item']
        item_type = "Film" if rec['type'] == 'movie' else "Série"
        print(f"{i}. {item['title']} - {item_type} - Score: {rec['score']:.2f}")
        print(f"   Genre: {', '.join(item.get('genre', []))}")
        print(f"   Ambiance: {', '.join(item.get('mood', []))}")
        print()

if __name__ == "__main__":
    test_recommendation_engine()
