#!/usr/bin/env python3
"""
Script de diagnostic pour les recommandations
"""

import sys
import os

# Ajouter le répertoire backend au chemin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Teste tous les imports nécessaires"""
    print("🔍 Test des imports...")
    
    try:
        print("  ✓ Import sys, os")
        
        # Test import de la base de données utilisateur
        from data.user_database import load_users
        print("  ✓ Import user_database")
        
        # Test import des fournisseurs API
        from src.api_providers.multi_api_manager import MultiAPIManager
        print("  ✓ Import multi_api_manager")
        
        # Test import du moteur de scoring
        from src.recommendation_scoring import RecommendationEngine, RecommendationScorer
        print("  ✓ Import recommendation_scoring")
        
        # Test import des utilitaires
        from src.recommendation_utils import (
            CacheManager, StreamingServiceMapper, ContentTypeConverter,
            GenreManager, RecommendationFormatter, PerformanceMonitor
        )
        print("  ✓ Import recommendation_utils")
        
        # Test import du moteur principal
        from src.recommendation_engine_v2 import modular_engine
        print("  ✓ Import moteur principal")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False

def test_api_keys():
    """Teste les clés API"""
    print("\n🔑 Test des clés API...")
    
    try:
        from config import TMDB_API_KEY, WATCHMODE_API_KEY
        print(f"  ✓ TMDB_API_KEY: {'***' + TMDB_API_KEY[-4:] if TMDB_API_KEY else 'NON DÉFINIE'}")
        print(f"  ✓ WATCHMODE_API_KEY: {'***' + WATCHMODE_API_KEY[-4:] if WATCHMODE_API_KEY else 'NON DÉFINIE'}")
        return True
    except ImportError:
        print("  ❌ Fichier config.py non trouvé")
        return False

def test_engine_initialization():
    """Teste l'initialisation du moteur"""
    print("\n🚀 Test d'initialisation du moteur...")
    
    try:
        from src.recommendation_engine_v2 import modular_engine
        
        # Tester les utilisateurs
        users = modular_engine.users
        print(f"  ✓ Utilisateurs chargés: {len(users)}")
        
        # Tester l'API manager
        providers = modular_engine.api_manager.active_providers
        print(f"  ✓ Fournisseurs API actifs: {providers}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur d'initialisation: {e}")
        return False

def test_recommendations():
    """Teste la génération de recommandations"""
    print("\n💡 Test de génération de recommandations...")
    
    try:
        from src.recommendation_engine_v2 import modular_engine
        
        # Utiliser le premier utilisateur disponible
        users = modular_engine.users
        if not users:
            print("  ❌ Aucun utilisateur disponible")
            return False
            
        test_user = users[0]
        user_id = test_user['id']
        
        print(f"  🧪 Test avec utilisateur ID: {user_id}")
        
        # Générer des recommandations
        recommendations = modular_engine.get_recommendations(
            user_id=user_id,
            n=3,
            content_type='all'
        )
        
        print(f"  ✓ Recommandations générées: {len(recommendations)}")
        
        if recommendations:
            print("  📋 Première recommandation:")
            first_rec = recommendations[0]
            print(f"    - Titre: {first_rec.get('item', {}).get('title', 'N/A')}")
            print(f"    - Type: {first_rec.get('type', 'N/A')}")
            print(f"    - Score: {first_rec.get('compatibility_score', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur de génération: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("  DIAGNOSTIC DU SYSTÈME DE RECOMMANDATIONS")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_api_keys,
        test_engine_initialization,
        test_recommendations
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("  RÉSUMÉ")
    print("=" * 50)
    
    if all(results):
        print("✅ Tous les tests sont passés!")
        print("Le système de recommandations devrait fonctionner.")
    else:
        print("❌ Certains tests ont échoué.")
        print("Vérifiez les erreurs ci-dessus.")
    
    print("\n🔧 Pour corriger les problèmes sur le serveur:")
    print("1. Assurez-vous que tous les modules sont installés")
    print("2. Vérifiez la configuration des clés API")
    print("3. Redémarrez le service backend")

if __name__ == "__main__":
    main()
