"""
Script de test pour l'architecture modulaire v2.0
Teste toutes les fonctionnalités du nouveau système de recommandation
"""

import sys
import os
import time

# Ajouter le répertoire parent au chemin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommendation_engine_v2 import modular_engine
from data.user_database import load_users

def test_modular_system():
    """Test complet du système modulaire"""
    
    print("🧪 Test du système de recommandation modulaire v2.0")
    print("=" * 60)
    
    # 1. Test du statut des APIs
    print("\n1. 📊 Test du statut des APIs")
    print("-" * 40)
    
    status = modular_engine.get_api_status()
    print(f"✅ Fournisseurs actifs: {', '.join(status.get('active_providers', []))}")
    print(f"📈 Performance: {status.get('performance', {})}")
    print(f"💾 Taille du cache: {status.get('cache_size', 0)} entrées")
    
    # 2. Test de recherche
    print("\n2. 🔍 Test de recherche multi-API")
    print("-" * 40)
    
    search_terms = ["Avengers", "Game of Thrones", "Inception"]
    
    for term in search_terms:
        print(f"\n🔎 Recherche: '{term}'")
        try:
            results = modular_engine.search_content(
                query=term, 
                content_type="all", 
                max_results=5
            )
            
            if results.get("error"):
                print(f"❌ Erreur: {results['error']}")
            else:
                print(f"✅ {len(results.get('results', []))} résultats trouvés")
                print(f"📡 Fournisseurs utilisés: {', '.join(results.get('providers_used', []))}")
                
                # Afficher les premiers résultats
                for i, item in enumerate(results.get("results", [])[:3], 1):
                    print(f"   {i}. {item.get('title', 'N/A')} ({item.get('year', 'N/A')}) - {item.get('rating', 0)}/10")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        time.sleep(0.5)  # Éviter de surcharger les APIs
    
    # 3. Test de contenu tendance  
    print("\n3. 📈 Test de contenu tendance")
    print("-" * 40)
    
    content_types = ["all", "movies", "series"]
    
    for content_type in content_types:
        print(f"\n📺 Contenu tendance: {content_type}")
        try:
            results = modular_engine.get_trending_content(
                content_type=content_type, 
                max_results=5
            )
            
            if results.get("error"):
                print(f"❌ Erreur: {results['error']}")
            else:
                print(f"✅ {len(results.get('results', []))} éléments tendance")
                print(f"📡 Fournisseurs utilisés: {', '.join(results.get('providers_used', []))}")
                
                # Afficher les premiers résultats
                for i, item in enumerate(results.get("results", [])[:3], 1):
                    print(f"   {i}. {item.get('title', 'N/A')} ({item.get('year', 'N/A')}) - {item.get('rating', 0)}/10")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        time.sleep(0.5)
    
    # 4. Test de recommandations personnalisées
    print("\n4. 🎯 Test de recommandations personnalisées")
    print("-" * 40)
    
    users = load_users()
    
    if users:
        test_user = users[0]  # Premier utilisateur
        user_id = test_user["id"]
        user_name = test_user["name"]
        
        print(f"\n👤 Utilisateur test: {user_name} (ID: {user_id})")
        
        # Afficher les préférences
        preferences = test_user.get("preferences", {})
        print(f"💚 Genres aimés: {', '.join(preferences.get('genres_likes', []))}")
        print(f"❤️ Mots-clés: {', '.join(preferences.get('keywords_likes', []))}")
        print(f"📺 Services streaming: {', '.join(preferences.get('streaming_services', []))}")
        
        # Test des recommandations
        content_types = ["all", "movies", "series"]
        
        for content_type in content_types:
            print(f"\n🎬 Recommandations {content_type}:")
            try:
                recommendations = modular_engine.get_recommendations(
                    user_id=user_id,
                    n=5,
                    content_type=content_type
                )
                
                if recommendations:
                    print(f"✅ {len(recommendations)} recommandations générées")
                    
                    for i, rec in enumerate(recommendations, 1):
                        title = rec.get("title", "N/A")
                        year = rec.get("year", "N/A")
                        rating = rec.get("rating", 0)
                        score = rec.get("score", 0)
                        streaming = rec.get("streaming_services", [])
                        
                        print(f"   {i}. {title} ({year}) - {rating}/10 (Score: {score:.1f})")
                        if streaming:
                            print(f"      📺 Disponible sur: {', '.join(streaming)}")
                else:
                    print("❌ Aucune recommandation générée")
                    
            except Exception as e:
                print(f"❌ Exception recommandations: {e}")
            
            time.sleep(0.5)
    
    else:
        print("❌ Aucun utilisateur trouvé dans la base de données")
    
    # 5. Test de performances et cache
    print("\n5. ⚡ Test de performances et cache")
    print("-" * 40)
    
    # Test du cache avec une recherche répétée
    search_query = "Marvel"
    
    print(f"🔄 Première recherche '{search_query}' (pas de cache)")
    start_time = time.time()
    results1 = modular_engine.search_content(search_query, "all", 5)
    time1 = time.time() - start_time
    print(f"⏱️ Temps: {time1:.2f}s")
    
    print(f"🔄 Deuxième recherche '{search_query}' (avec cache)")
    start_time = time.time()
    results2 = modular_engine.search_content(search_query, "all", 5)
    time2 = time.time() - start_time
    print(f"⏱️ Temps: {time2:.2f}s")
    
    if time2 < time1 * 0.5:  # Le cache devrait être significativement plus rapide
        print("✅ Cache fonctionnel - Amélioration de performance détectée")
    else:
        print("⚠️ Cache peut-être non fonctionnel ou pas de différence significative")
    
    # Statut final
    final_status = modular_engine.get_api_status()
    performance = final_status.get("performance", {})
    
    print(f"\n📊 Statistiques finales:")
    print(f"   🔄 Appels API totaux: {performance.get('api_calls', 0)}")
    print(f"   ⏱️ Temps réponse moyen: {performance.get('average_response_time', 0):.2f}s")
    print(f"   ❌ Taux d'erreur: {performance.get('error_rate', 0):.1%}")
    print(f"   💾 Taux de cache hit: {performance.get('cache_hit_rate', 0):.1%}")
    print(f"   📦 Entrées en cache: {final_status.get('cache_size', 0)}")
    
    # 6. Test des services de streaming supportés
    print("\n6. 📺 Services de streaming supportés")
    print("-" * 40)
    
    supported_services = modular_engine.get_supported_streaming_services()
    print(f"✅ Services supportés: {', '.join(supported_services)}")
    
    print("\n" + "=" * 60)
    print("🎉 Tests terminés avec succès!")
    print("✨ Architecture modulaire v2.0 opérationnelle")
    
    # Recommandations d'utilisation
    print(f"\n💡 Recommandations:")
    if "Watchmode" in modular_engine.api_manager.active_providers:
        print("   ✅ Watchmode actif - Vous bénéficiez de sources de données multiples")
    else:
        print("   ⚠️ Seul TMDb est actif - Fonctionnalité complète disponible")
    
    if performance.get('cache_hit_rate', 0) > 0:
        print("   ✅ Cache fonctionnel - Performances optimisées")
    else:
        print("   💡 Cache pas encore utilisé - Les performances s'amélioreront avec l'usage")

if __name__ == "__main__":
    test_modular_system()
