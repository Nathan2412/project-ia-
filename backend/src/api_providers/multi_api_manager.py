"""
Gestionnaire multi-API version 2.0
Architecture modulaire pour gérer plusieurs fournisseurs d'API de manière optimisée
"""

import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any, Union
import time

from .tmdb_provider import TMDbProvider
from .watchmode_provider import WatchmodeProvider

class MultiAPIManager:
    """Gestionnaire centralisé pour tous les fournisseurs d'API"""
    
    def __init__(self, tmdb_key: str, watchmode_key: str = "", rapidapi_key: str = ""):
        self.providers = {}
        self.active_providers = []
        
        # Initialiser les fournisseurs
        if tmdb_key:
            self.providers["TMDb"] = TMDbProvider(tmdb_key)
        
        # Préférer la clé Watchmode directe si disponible
        if watchmode_key:
            self.providers["Watchmode"] = WatchmodeProvider(watchmode_key, use_rapidapi=False)
        elif rapidapi_key:
            self.providers["Watchmode"] = WatchmodeProvider(rapidapi_key, use_rapidapi=True)
        
        # Tester les connexions
        self._test_providers()
    
    def _test_providers(self):
        """Teste la connexion de tous les fournisseurs"""
        self.active_providers = []
        
        for name, provider in self.providers.items():
            try:
                if provider.test_connection():
                    self.active_providers.append(name)
                    print(f"✅ {name}: Connecté")
                else:
                    print(f"❌ {name}: Connexion échouée")
            except Exception as e:
                print(f"❌ {name}: Erreur - {e}")
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Retourne le statut de tous les fournisseurs"""
        status = {}
        
        for name, provider in self.providers.items():
            is_active = name in self.active_providers
            status[name] = {
                "available": is_active,
                "connection": is_active,
                "name": provider.name if hasattr(provider, 'name') else name
            }
        
        return {
            "provider_status": status,
            "active_providers": self.active_providers,
            "total_providers": len(self.providers)
        }
    
    def search_content_parallel(self, query: str, content_type: str = "all", 
                              max_results: int = 20) -> Dict[str, Any]:
        """
        Recherche parallèle sur tous les fournisseurs actifs
        
        Args:
            query: Terme de recherche
            content_type: Type de contenu ('movie', 'tv', 'all')
            max_results: Nombre maximum de résultats
            
        Returns:
            Résultats combinés et dédupliqués
        """
        if not self.active_providers:
            return {
                "error": "Aucun fournisseur d'API disponible",
                "results": [],
                "providers_used": []
            }
        
        all_results = []
        providers_used = []
        errors = []
        
        # Exécution parallèle des recherches
        with ThreadPoolExecutor(max_workers=len(self.active_providers)) as executor:
            # Lancer les recherches
            future_to_provider = {}
            for provider_name in self.active_providers:
                provider = self.providers[provider_name]
                future = executor.submit(provider.search_content, query, content_type)
                future_to_provider[future] = provider_name
            
            # Collecter les résultats
            for future in as_completed(future_to_provider):
                provider_name = future_to_provider[future]
                try:
                    result = future.result(timeout=10)  # Timeout de 10 secondes
                    
                    if "error" in result:
                        errors.append(f"{provider_name}: {result['error']}")
                    else:
                        all_results.extend(result.get("results", []))
                        providers_used.append(provider_name)
                        
                except Exception as e:
                    errors.append(f"{provider_name}: Exception - {str(e)}")
        
        # Déduplication et tri des résultats
        deduplicated_results = self._deduplicate_and_merge(all_results)
        
        # Tri par pertinence (rating + popularité)
        sorted_results = sorted(
            deduplicated_results,
            key=lambda x: (x.get("rating", 0) * 0.7 + 
                          min(x.get("popularity", 0) / 100, 5) * 0.3),
            reverse=True
        )
        
        return {
            "results": sorted_results[:max_results],
            "total_results": len(sorted_results),
            "providers_used": providers_used,
            "errors": errors if errors else None
        }
    
    def get_trending_parallel(self, content_type: str = "all", 
                            max_results: int = 20) -> Dict[str, Any]:
        """
        Récupération parallèle du contenu tendance
        
        Args:
            content_type: Type de contenu ('movie', 'tv', 'all')
            max_results: Nombre maximum de résultats
            
        Returns:
            Contenu tendance combiné
        """
        if not self.active_providers:
            return {
                "error": "Aucun fournisseur d'API disponible",
                "results": [],
                "providers_used": []
            }
        
        all_results = []
        providers_used = []
        errors = []
        
        # Exécution parallèle
        with ThreadPoolExecutor(max_workers=len(self.active_providers)) as executor:
            future_to_provider = {}
            for provider_name in self.active_providers:
                provider = self.providers[provider_name]
                if hasattr(provider, 'get_trending'):
                    future = executor.submit(provider.get_trending, content_type)
                    future_to_provider[future] = provider_name
            
            # Collecter les résultats
            for future in as_completed(future_to_provider):
                provider_name = future_to_provider[future]
                try:
                    result = future.result(timeout=10)
                    
                    if "error" in result:
                        errors.append(f"{provider_name}: {result['error']}")
                    else:
                        all_results.extend(result.get("results", []))
                        providers_used.append(provider_name)
                        
                except Exception as e:
                    errors.append(f"{provider_name}: Exception - {str(e)}")
        
        # Déduplication et tri
        deduplicated_results = self._deduplicate_and_merge(all_results)
        
        # Tri par rating et popularité
        sorted_results = sorted(
            deduplicated_results,
            key=lambda x: (x.get("rating", 0) * 0.6 + 
                          min(x.get("popularity", 0) / 100, 4) * 0.4),
            reverse=True
        )
        
        return {
            "results": sorted_results[:max_results],
            "providers_used": providers_used,
            "errors": errors if errors else None
        }
    
    def get_enhanced_details(self, item_id: int, content_type: str, 
                           provider: str = "TMDb") -> Dict[str, Any]:
        """
        Récupère les détails enrichis d'un élément
        
        Args:
            item_id: ID de l'élément
            content_type: Type de contenu ('movie' ou 'tv')
            provider: Fournisseur principal à utiliser
            
        Returns:
            Détails enrichis avec informations de streaming
        """
        if provider not in self.active_providers:
            provider = self.active_providers[0] if self.active_providers else None
        
        if not provider:
            return {"error": "Aucun fournisseur disponible"}
        
        # Récupérer les détails du fournisseur principal
        main_provider = self.providers[provider]
        
        if provider == "TMDb":
            details = main_provider.get_details(item_id, content_type)
        else:
            details = main_provider.get_details(item_id)
        
        if "error" in details:
            return details
        
        # Enrichir avec les informations de streaming si Watchmode est disponible
        if "Watchmode" in self.active_providers and provider == "TMDb":
            try:
                watchmode_provider = self.providers["Watchmode"]
                # Rechercher l'élément sur Watchmode pour obtenir son ID
                search_query = details.get("title", details.get("name", ""))
                watchmode_search = watchmode_provider.search_content(search_query, content_type)
                
                if not watchmode_search.get("error") and watchmode_search.get("results"):
                    # Prendre le premier résultat qui correspond
                    for result in watchmode_search["results"][:3]:  # Vérifier les 3 premiers
                        if (result.get("title", "").lower() == search_query.lower() or
                            abs(result.get("rating", 0) - details.get("vote_average", 0)) < 1.0):
                            
                            # Récupérer les sources de streaming
                            streaming_info = watchmode_provider.get_streaming_sources(result["id"])
                            if not streaming_info.get("error"):
                                details["enhanced_streaming"] = streaming_info
                            break
                            
            except Exception as e:
                print(f"Erreur enrichissement Watchmode: {e}")
        
        return details
    
    def _deduplicate_and_merge(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Déduplique et fusionne les résultats de différents fournisseurs
        
        Args:
            results: Liste des résultats de tous les fournisseurs
            
        Returns:
            Liste dédupliquée et fusionnée
        """
        # Dictionnaire pour stocker les éléments uniques
        unique_items = {}
        
        for item in results:
            # Clés de déduplication possibles
            title = item.get("title", "").lower().strip()
            year = item.get("year", "")
            media_type = item.get("media_type", "")
            
            # Créer une clé unique
            unique_key = f"{title}_{year}_{media_type}"
            
            if unique_key not in unique_items:
                unique_items[unique_key] = item
            else:
                # Fusionner les informations (prendre les meilleures données)
                existing = unique_items[unique_key]
                
                # Prendre la meilleure note (TMDb généralement plus fiable)
                if item.get("provider") == "TMDb" and existing.get("provider") != "TMDb":
                    existing["rating"] = item.get("rating", existing.get("rating", 0))
                
                # Fusionner les informations complémentaires
                if item.get("description") and len(item.get("description", "")) > len(existing.get("description", "")):
                    existing["description"] = item.get("description")
                
                # Ajouter les IDs de différents fournisseurs
                if item.get("watchmode_id"):
                    existing["watchmode_id"] = item.get("watchmode_id")
                if item.get("imdb_id"):
                    existing["imdb_id"] = item.get("imdb_id")
                if item.get("tmdb_id"):
                    existing["tmdb_id"] = item.get("tmdb_id")
        
        return list(unique_items.values())
    
    def search_with_fallback(self, query: str, content_type: str = "all", 
                           primary_provider: str = "TMDb") -> Dict[str, Any]:
        """
        Recherche avec système de fallback en cas d'échec du fournisseur principal
        
        Args:
            query: Terme de recherche
            content_type: Type de contenu
            primary_provider: Fournisseur principal à essayer en premier
            
        Returns:
            Résultats avec indication du fournisseur utilisé
        """
        # Essayer le fournisseur principal d'abord
        if primary_provider in self.active_providers:
            try:
                provider = self.providers[primary_provider]
                result = provider.search_content(query, content_type)
                
                if not result.get("error") and result.get("results"):
                    return {
                        **result,
                        "provider_used": primary_provider,
                        "fallback_used": False
                    }
            except Exception as e:
                print(f"Erreur avec fournisseur principal {primary_provider}: {e}")
        
        # Fallback vers les autres fournisseurs
        for provider_name in self.active_providers:
            if provider_name != primary_provider:
                try:
                    provider = self.providers[provider_name]
                    result = provider.search_content(query, content_type)
                    
                    if not result.get("error") and result.get("results"):
                        return {
                            **result,
                            "provider_used": provider_name,
                            "fallback_used": True,
                            "fallback_reason": f"Échec de {primary_provider}"
                        }
                except Exception as e:
                    print(f"Erreur avec fournisseur fallback {provider_name}: {e}")
        
        return {
            "error": "Tous les fournisseurs ont échoué",
            "results": [],
            "providers_tried": self.active_providers
        }
