"""
Moteur de recommandation modulaire v2.0
Architecture basée sur des composants séparés pour une meilleure maintenabilité
"""

import sys
import os
from typing import Dict, List, Any, Optional

# Ajouter le répertoire parent au chemin
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import des modules de base
from data.user_database import load_users, update_user
from data.movies_series_database import STREAMING_SERVICES

# Import des nouveaux modules modulaires
from src.api_providers.multi_api_manager import MultiAPIManager
from src.recommendation_scoring import RecommendationEngine, RecommendationScorer
from src.recommendation_utils import (
    CacheManager, StreamingServiceMapper, ContentTypeConverter,
    GenreManager, RecommendationFormatter, PerformanceMonitor
)

# Import de la configuration
try:
    from config import TMDB_API_KEY, WATCHMODE_API_KEY, RAPIDAPI_KEY, API_PROVIDERS
except ImportError:
    TMDB_API_KEY = "f584c416fc7b0c9c1591acabafc13a72"
    WATCHMODE_API_KEY = ""
    RAPIDAPI_KEY = ""
    API_PROVIDERS = {}

class ModularRecommendationEngine:
    """Moteur de recommandation principal avec architecture modulaire"""
    
    def __init__(self):
        # Initialiser les composants
        self.api_manager = MultiAPIManager(TMDB_API_KEY, WATCHMODE_API_KEY, RAPIDAPI_KEY)
        self.scorer = RecommendationScorer()
        self.recommendation_engine = RecommendationEngine(self.api_manager, self.scorer)
        self.cache_manager = CacheManager(cache_duration_minutes=30)
        self.performance_monitor = PerformanceMonitor()
        
        # Charger les utilisateurs
        self.users = load_users()
        
        print(f"🚀 Moteur de recommandation modulaire initialisé")
        print(f"📊 Fournisseurs actifs: {', '.join(self.api_manager.active_providers)}")
    
    def get_recommendations(self, user_id: int, n: int = 5, content_type: str = 'all', 
                          streaming_services: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Obtient des recommandations pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            n: Nombre de recommandations
            content_type: Type de contenu ('movies', 'series', 'all')
            streaming_service: Service de streaming spécifique
            
        Returns:
            Liste de recommandations formatées
        """
        import time
        start_time = time.time()
        
        try:
            print(f"🔍 DEBUG Engine - get_recommendations called:")
            print(f"  - user_id: {user_id}")
            print(f"  - n: {n}")
            print(f"  - content_type: {content_type}")
            print(f"  - streaming_services: {streaming_services}")
            
            # Trouver l'utilisateur
            user = self._get_user_by_id(user_id)
            if not user:
                print(f"❌ Utilisateur {user_id} non trouvé")
                return []
            
            print(f"✅ Utilisateur trouvé: {user.get('name', 'Sans nom')}")
            
            # Préparer les préférences utilisateur
            user_preferences = self._prepare_user_preferences(user, streaming_services)
            print(f"✅ Préférences préparées: {list(user_preferences.keys())}")
            
            # Convertir le type de contenu
            internal_content_type = ContentTypeConverter.convert_type(
                content_type, "external", "internal"
            )
            
            # Vérifier le cache
            cache_key = self.cache_manager.get_cache_key(
                user_id, n, internal_content_type, ",".join(streaming_services) if streaming_services else ""
            )
            
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                self.performance_monitor.record_cache_hit()
                return cached_result
            
            self.performance_monitor.record_cache_miss()
            
            # Générer les recommandations
            recommendations = self.recommendation_engine.get_personalized_recommendations(
                user_preferences=user_preferences,
                content_type=internal_content_type,
                max_results=n
            )
            
            # Formater les recommandations
            formatted_recommendations = RecommendationFormatter.format_recommendation_list(
                recommendations
            )
            
            # Filtrer par services de streaming si spécifiés
            if streaming_services:
                normalized_services = [StreamingServiceMapper.normalize_service_name(s) for s in streaming_services]
                formatted_recommendations = [
                    rec for rec in formatted_recommendations
                    if any(service in rec.get("streaming_services", []) for service in normalized_services)
                ]
            
            # Mettre en cache
            self.cache_manager.set(cache_key, formatted_recommendations)
            
            # Enregistrer les métriques
            response_time = time.time() - start_time
            self.performance_monitor.record_api_call(response_time, True)
            
            return formatted_recommendations[:n]
            
        except Exception as e:
            print(f"❌ Erreur génération recommandations: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            
            # Afficher la stack trace complète pour débugger
            import traceback
            traceback.print_exc()
            
            response_time = time.time() - start_time
            self.performance_monitor.record_api_call(response_time, False)
            return []
    
    def search_content(self, query: str, content_type: str = "all", 
                      max_results: int = 20) -> Dict[str, Any]:
        """
        Recherche de contenu via les APIs
        
        Args:
            query: Terme de recherche
            content_type: Type de contenu
            max_results: Nombre maximum de résultats
            
        Returns:
            Résultats de recherche avec métadonnées
        """
        import time
        start_time = time.time()
        
        try:
            # Vérifier le cache
            cache_key = self.cache_manager.get_cache_key(
                "search", query, content_type, max_results
            )
            
            cached_result = self.cache_manager.get(cache_key) 
            if cached_result:
                self.performance_monitor.record_cache_hit()
                return cached_result
            
            self.performance_monitor.record_cache_miss()
            
            # Convertir le type de contenu pour les APIs
            api_content_type = ContentTypeConverter.convert_type(
                content_type, "external", "internal"
            )
            
            # Effectuer la recherche
            results = self.api_manager.search_content_parallel(
                query=query,
                content_type=api_content_type,
                max_results=max_results
            )
            
            # Formater les résultats
            if not results.get("error") and results.get("results"):
                formatted_results = []
                for item in results["results"]:
                    formatted_item = self._format_search_item(item)
                    if formatted_item:
                        formatted_results.append(formatted_item)
                
                response = {
                    "results": formatted_results,
                    "total_results": len(formatted_results),
                    "providers_used": results.get("providers_used", []),
                    "query": query,
                    "content_type": content_type
                }
                
                # Mettre en cache
                self.cache_manager.set(cache_key, response)
                
                # Métriques
                response_time = time.time() - start_time
                self.performance_monitor.record_api_call(response_time, True)
                
                return response
            else:
                error_response = {
                    "error": results.get("error", "Aucun résultat trouvé"),
                    "results": [],
                    "query": query
                }
                
                response_time = time.time() - start_time
                self.performance_monitor.record_api_call(response_time, False)
                
                return error_response
                
        except Exception as e:
            print(f"❌ Erreur recherche: {e}")
            response_time = time.time() - start_time
            self.performance_monitor.record_api_call(response_time, False)
            
            return {
                "error": f"Erreur lors de la recherche: {str(e)}",
                "results": [],
                "query": query
            }
    
    def get_trending_content(self, content_type: str = "all", 
                           max_results: int = 20) -> Dict[str, Any]:
        """
        Récupère le contenu tendance
        
        Args:
            content_type: Type de contenu
            max_results: Nombre maximum de résultats
            
        Returns:
            Contenu tendance avec métadonnées
        """
        import time
        start_time = time.time()
        
        try:
            # Cache
            cache_key = self.cache_manager.get_cache_key(
                "trending", content_type, max_results
            )
            
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                self.performance_monitor.record_cache_hit()
                return cached_result
            
            self.performance_monitor.record_cache_miss()
            
            # Convertir le type
            api_content_type = ContentTypeConverter.convert_type(
                content_type, "external", "internal"
            )
            
            # Récupérer le contenu tendance
            results = self.api_manager.get_trending_parallel(
                content_type=api_content_type,
                max_results=max_results
            )
            
            # Formater
            if not results.get("error") and results.get("results"):
                formatted_results = []
                for item in results["results"]:
                    formatted_item = self._format_search_item(item)
                    if formatted_item:
                        formatted_results.append(formatted_item)

                # Enrichir chaque recommandation avec les détails TMDb si provider = TMDb
                tmdb_provider = self.api_manager.providers.get("TMDb")
                enriched_recommendations = []
                for rec in formatted_results:
                    item = rec.get("item", rec)
                    if item.get("provider") == "TMDb" and tmdb_provider:
                        details = tmdb_provider.get_details(item.get("id"), item.get("media_type", "movie"))
                        rec["detailed_info"] = details
                    enriched_recommendations.append(rec)

                # Cache et retour des résultats
                response_time = time.time() - start_time
                self.performance_monitor.record_api_call(response_time, True)
                
                result = {
                    "results": enriched_recommendations,
                    "content_type": content_type,
                    "total_results": len(enriched_recommendations)
                }
                
                self.cache_manager.set(cache_key, result)
                return result
            else:
                # Aucun résultat trouvé
                response_time = time.time() - start_time
                self.performance_monitor.record_api_call(response_time, True)
                return {
                    "results": [],
                    "content_type": content_type,
                    "total_results": 0
                }

                
        except Exception as e:
            print(f"❌ Erreur contenu tendance: {e}")
            response_time = time.time() - start_time
            self.performance_monitor.record_api_call(response_time, False)
            
            return {
                "error": f"Erreur lors de la récupération: {str(e)}",
                "results": [],
                "content_type": content_type
            }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Retourne le statut des APIs et les métriques de performance"""
        status = self.api_manager.get_provider_status()
        performance_stats = self.performance_monitor.get_stats()
        
        return {
            **status,
            "performance": performance_stats,
            "cache_size": len(self.cache_manager.cache)
        }
    
    def update_user_history(self, user_id: int, item_id: str) -> bool:
        """Met à jour l'historique d'un utilisateur"""
        try:
            # Recharger les utilisateurs
            current_users = load_users()
            
            for user in current_users:
                if user['id'] == user_id:
                    if 'history' not in user:
                        user['history'] = []
                    
                    if item_id not in user['history']:
                        user['history'].append(item_id)
                        
                        # Mettre à jour la liste globale
                        for i, u in enumerate(self.users):
                            if u['id'] == user_id:
                                self.users[i] = user
                                break
                        
                        # Sauvegarder
                        success = update_user(user)
                        
                        # Invalider le cache pour cet utilisateur
                        self._invalidate_user_cache(user_id)
                        
                        return success
                        
            return False
            
        except Exception as e:
            print(f"❌ Erreur mise à jour historique: {e}")
            return False
    
    def clear_cache(self):
        """Vide le cache"""
        self.cache_manager.cache.clear()
        print("🧹 Cache vidé")
    
    def get_supported_streaming_services(self) -> List[str]:
        """Retourne la liste des services de streaming supportés"""
        return StreamingServiceMapper.get_supported_services()
    
    def _get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Trouve un utilisateur par son ID"""
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None
    
    def _prepare_user_preferences(self, user: Dict[str, Any],
                                streaming_services: Optional[List[str]] = None) -> Dict[str, Any]:
        """Prépare les préférences utilisateur pour le moteur de recommandation"""
        preferences = user.get('preferences', {}).copy()
        # L'historique peut être stocké soit comme liste d'IDs (legacy),
        # soit comme liste d'objets {id, title, content_type} (nouveau format)
        watch_history = preferences.get('watch_history') or user.get('history', [])
        history_ids = []
        for h in watch_history:
            if isinstance(h, dict):
                if h.get('id') is not None:
                    history_ids.append(str(h['id']))
            else:
                history_ids.append(str(h))
        preferences['history'] = history_ids
        
        # Normaliser les genres
        if 'genres_likes' in preferences:
            preferences['genres_likes'] = [
                GenreManager.normalize_genre(genre) or genre
                for genre in preferences['genres_likes']
            ]
        
        if 'genres_dislikes' in preferences:
            preferences['genres_dislikes'] = [
                GenreManager.normalize_genre(genre) or genre
                for genre in preferences['genres_dislikes']
            ]
        
        # Normaliser les services de streaming
        if 'streaming_services' in preferences:
            preferences['streaming_services'] = [
                StreamingServiceMapper.normalize_service_name(service)
                for service in preferences['streaming_services']
            ]
        
        # Ajouter les services spécifiques si demandés
        if streaming_services:
            normalized_services = [StreamingServiceMapper.normalize_service_name(s) for s in streaming_services]
            preferences['filter_by_streaming_services'] = normalized_services
        
        return preferences
    
    def _format_search_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Formate un élément de recherche pour l'API"""
        try:
            formatted = {
                "id": item.get("id"),
                "title": item.get("title", "Sans titre"),
                "year": item.get("year", ""),
                "rating": round(item.get("rating", 0), 1),
                "description": item.get("description", "Pas de description disponible"),
                "type": "movie" if item.get("media_type") == "movie" else "series",
                "provider": item.get("provider", "Unknown"),
                "popularity": item.get("popularity", 0)
            }
            
            # Images
            if item.get("poster_path"):
                formatted["poster_url"] = f"https://image.tmdb.org/t/p/w500{item['poster_path']}"
            
            # Genres
            if "genre_names" in item:
                formatted["genres"] = item["genre_names"]
            elif "genre_ids" in item:
                # Conversion basique des IDs de genres TMDb
                genre_map = {
                    28: "Action", 18: "Drama", 35: "Comedy", 80: "Crime",
                    99: "Documentary", 878: "Science Fiction", 53: "Thriller",
                    16: "Animation", 10749: "Romance", 27: "Horror"
                }
                formatted["genres"] = [
                    genre_map.get(gid, "Unknown") for gid in item["genre_ids"]
                ]
            else:
                formatted["genres"] = []
            
            return formatted
            
        except Exception as e:
            print(f"❌ Erreur formatage item: {e}")
            return None
    
    def _invalidate_user_cache(self, user_id: int):
        """Invalide le cache pour un utilisateur spécifique"""
        keys_to_remove = []
        for key in self.cache_manager.cache.keys():
            if str(user_id) in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache_manager.cache[key]

# Instance globale du moteur de recommandation
modular_engine = ModularRecommendationEngine()

# Fonctions de compatibilité avec l'ancien système
def get_recommendations(user_id: int, n: int = 5, content_type: str = 'all',
                       streaming_service: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fonction de compatibilité pour l'ancienne API"""
    # Convertir le paramètre single vers list pour correspondre à la nouvelle signature
    services_list = [streaming_service] if streaming_service else None
    return modular_engine.get_recommendations(user_id, n, content_type, services_list)

def search_multi_api(query: str, content_type: str = "all", max_results: int = 20) -> List[Dict[str, Any]]:
    """Fonction de compatibilité pour la recherche multi-API"""
    results = modular_engine.search_content(query, content_type, max_results)
    return results.get("results", [])

def get_trending_multi_api(content_type: str = "all", max_results: int = 20) -> List[Dict[str, Any]]:
    """Fonction de compatibilité pour le contenu tendance"""
    results = modular_engine.get_trending_content(content_type, max_results)
    return results.get("results", [])

def update_user_history(user_id: int, item_id: str) -> bool:
    """Fonction de compatibilité pour la mise à jour de l'historique"""
    return modular_engine.update_user_history(user_id, item_id)

def check_api_key(force_ask: bool = False) -> bool:
    """Fonction de compatibilité pour la vérification des clés API"""
    status = modular_engine.get_api_status()
    return len(status.get("active_providers", [])) > 0
