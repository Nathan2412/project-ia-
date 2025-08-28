#!/usr/bin/env python3
"""
Test simple des recommandations en local
"""

import sys
import os

# Ajouter le répertoire backend au chemin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_recommendations_local():
    """Test des recommandations en local"""
    try:
        print("🧪 Test des recommandations en local...")
        
        # Import du moteur
        from src.recommendation_engine_v2 import modular_engine
        
        # Récupérer un utilisateur de test
        users = modular_engine.users
        if not users:
            print("❌ Aucun utilisateur trouvé")
            return
        
        test_user = users[0]  # Premier utilisateur
        user_id = test_user['id']
        
        print(f"👤 Test avec utilisateur: {test_user.get('name', 'Sans nom')} (ID: {user_id})")
        print(f"📋 Préférences utilisateur: {test_user.get('preferences', {})}")
        
        # Test de recommandations
        recommendations = modular_engine.get_recommendations(
            user_id=user_id,
            n=5,
            content_type='all',
            streaming_services=None
        )
        
        print(f"✅ Recommandations générées: {len(recommendations)}")
        
        if recommendations:
            print("\n📺 Premières recommandations:")
            for i, rec in enumerate(recommendations[:3]):
                item = rec.get('item', {})
                print(f"  {i+1}. {item.get('title', 'Sans titre')} ({rec.get('type', 'N/A')}) - Score: {rec.get('compatibility_score', 'N/A')}")
        else:
            print("❌ Aucune recommandation générée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recommendations_local()
