"""
Module de gestion des APIs multiples pour les recommandations.
Ce module permet d'interroger plusieurs sources (TMDb, Watchmode, etc.) 
et de combiner les résultats pour de meilleures recommandations.
"""

import requests
import json
import time
from typing import List, Dict, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration des APIs
try:
    from config import TMDB_API_KEY, WATCHMODE_API_KEY
except ImportError:
    # Clés par défaut si le fichier config n'existe pas
    TMDB_API_KEY = "f584c416fc7b0c9c1591acabafc13a72"
    WATCHMODE_API_KEY = ""  # À configurer

# URLs de base des APIs
TMDB_BASE_URL = "https://api.themoviedb.org/3"
WATCHMODE_BASE_URL = "https://api.watchmode.com/v1"

class APIProvider:
    """Classe de base pour les fournisseurs d'API."""
    
    def __init__(self, name: str, base_url: str, api_key: str):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.is_available = bool(api_key)
    
    def test_connection(self) -> bool:
        """Teste la connexion à l'API."""
        return self.is_available

class TMDbProvider(APIProvider):
    """Fournisseur pour l'API TMDb."""
    
    def __init__(self):
        super().__init__("TMDb", TMDB_BASE_URL, TMDB_API_KEY)
    
    def search_content(self, query: str, content_type: str = "all", page: int = 1) -> Dict:
        """
        Recherche de contenu sur TMDb.
        
        Args:
            query: Terme de recherche
            content_type: 'movie', 'tv', ou 'all'
            page: Numéro de page
        
        Returns:
            Dict: Résultats de recherche formatés
        """
        if not self.is_available:
            return {"results": [], "provider": self.name, "error": "API key not available"}
        
        try:
            if content_type == "all":
                # Recherche multimédia
                url = f"{self.base_url}/search/multi"
            elif content_type == "movie":
                url = f"{self.base_url}/search/movie"
            elif content_type == "tv":
                url = f"{self.base_url}/search/tv"
            else:
                url = f"{self.base_url}/search/multi"
            
            params = {
                "api_key": self.api_key,
                "query": query,
                "page": page,
                "language": "fr-FR"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                "results": self._format_tmdb_results(data.get("results", [])),
                "provider": self.name,
                "total_pages": data.get("total_pages", 1),
                "total_results": data.get("total_results", 0)
            }
            
        except Exception as e:
            return {
                "results": [],
                "provider": self.name,
                "error": f"TMDb API error: {str(e)}"
            }
    
    def get_trending(self, media_type: str = "all", time_window: str = "week") -> Dict:
        """
        Récupère le contenu tendance depuis TMDb.
        
        Args:
            media_type: 'all', 'movie', ou 'tv'
            time_window: 'day' ou 'week'
        
        Returns:
            Dict: Contenu tendance formaté
        """
        if not self.is_available:
            return {"results": [], "provider": self.name, "error": "API key not available"}
        
        try:
            url = f"{self.base_url}/trending/{media_type}/{time_window}"
            params = {
                "api_key": self.api_key,
                "language": "fr-FR"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                "results": self._format_tmdb_results(data.get("results", [])),
                "provider": self.name
            }
            
        except Exception as e:
            return {
                "results": [],
                "provider": self.name,
                "error": f"TMDb trending error: {str(e)}"
            }
    
    def get_details(self, content_id: int, media_type: str) -> Dict:
        """
        Récupère les détails d'un contenu depuis TMDb.
        
        Args:
            content_id: ID du contenu
            media_type: 'movie' ou 'tv'
        
        Returns:
            Dict: Détails du contenu
        """
        if not self.is_available:
            return {"error": "API key not available"}
        
        try:
            url = f"{self.base_url}/{media_type}/{content_id}"
            params = {
                "api_key": self.api_key,
                "language": "fr-FR",
                "append_to_response": "credits,videos,watch/providers"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_tmdb_details(data, media_type)
            
        except Exception as e:
            return {"error": f"TMDb details error: {str(e)}"}
    
    def _format_tmdb_results(self, results: List[Dict]) -> List[Dict]:
        """Formate les résultats TMDb dans un format standardisé."""
        formatted = []
        
        for item in results:
            media_type = item.get("media_type", "movie")
            if "first_air_date" in item:
                media_type = "tv"
            elif "release_date" in item:
                media_type = "movie"
            
            formatted_item = {
                "id": item.get("id"),
                "title": item.get("title") or item.get("name"),
                "original_title": item.get("original_title") or item.get("original_name"),
                "overview": item.get("overview", ""),
                "poster_path": item.get("poster_path"),
                "backdrop_path": item.get("backdrop_path"),
                "vote_average": item.get("vote_average", 0),
                "vote_count": item.get("vote_count", 0),
                "popularity": item.get("popularity", 0),
                "genre_ids": item.get("genre_ids", []),
                "adult": item.get("adult", False),
                "media_type": media_type,
                "release_date": item.get("release_date") or item.get("first_air_date"),
                "provider": self.name
            }
            formatted.append(formatted_item)
        
        return formatted
    
    def _format_tmdb_details(self, data: Dict, media_type: str) -> Dict:
        """Formate les détails TMDb dans un format standardisé."""
        return {
            "id": data.get("id"),
            "title": data.get("title") or data.get("name"),
            "original_title": data.get("original_title") or data.get("original_name"),
            "overview": data.get("overview", ""),
            "poster_path": data.get("poster_path"),
            "backdrop_path": data.get("backdrop_path"),
            "vote_average": data.get("vote_average", 0),
            "vote_count": data.get("vote_count", 0),
            "popularity": data.get("popularity", 0),
            "genres": [g.get("name", "") for g in data.get("genres", [])],
            "runtime": data.get("runtime") or data.get("episode_run_time", [0])[0] if data.get("episode_run_time") else 0,
            "release_date": data.get("release_date") or data.get("first_air_date"),
            "status": data.get("status", ""),
            "media_type": media_type,
            "production_companies": [c.get("name", "") for c in data.get("production_companies", [])],
            "credits": data.get("credits", {}),
            "videos": data.get("videos", {}),
            "watch_providers": data.get("watch/providers", {}),
            "provider": self.name
        }

class WatchmodeProvider(APIProvider):
    """Fournisseur pour l'API Watchmode."""
    
    def __init__(self):
        super().__init__("Watchmode", WATCHMODE_BASE_URL, WATCHMODE_API_KEY)
    
    def search_content(self, query: str, content_type: str = "all", page: int = 1) -> Dict:
        """
        Recherche de contenu sur Watchmode.
        
        Args:
            query: Terme de recherche
            content_type: 'movie', 'tv_series', ou 'all'
            page: Numéro de page (Watchmode utilise un système différent)
        
        Returns:
            Dict: Résultats de recherche formatés
        """
        if not self.is_available:
            return {"results": [], "provider": self.name, "error": "API key not available"}
        
        try:
            url = f"{self.base_url}/search/"
            params = {
                "apikey": self.api_key,
                "search_field": "name",
                "search_value": query
            }
            
            # Ajouter le type de contenu si spécifié
            if content_type != "all":
                if content_type == "tv":
                    content_type = "tv_series"
                params["types"] = content_type
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                "results": self._format_watchmode_results(data.get("titles", [])),
                "provider": self.name,
                "total_results": len(data.get("titles", []))
            }
            
        except Exception as e:
            return {
                "results": [],
                "provider": self.name,
                "error": f"Watchmode API error: {str(e)}"
            }
    
    def get_trending(self, media_type: str = "all", limit: int = 20) -> Dict:
        """
        Récupère le contenu populaire depuis Watchmode.
        
        Args:
            media_type: 'all', 'movie', ou 'tv_series'
            limit: Nombre de résultats à retourner
        
        Returns:
            Dict: Contenu populaire formaté
        """
        if not self.is_available:
            return {"results": [], "provider": self.name, "error": "API key not available"}
        
        try:
            url = f"{self.base_url}/list-titles/"
            params = {
                "apikey": self.api_key,
                "limit": limit
            }
            
            if media_type != "all":
                if media_type == "tv":
                    media_type = "tv_series"
                params["types"] = media_type
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                "results": self._format_watchmode_results(data.get("titles", [])),
                "provider": self.name
            }
            
        except Exception as e:
            return {
                "results": [],
                "provider": self.name,
                "error": f"Watchmode trending error: {str(e)}"
            }
    
    def get_details(self, content_id: Union[int, str]) -> Dict:
        """
        Récupère les détails d'un contenu depuis Watchmode.
        
        Args:
            content_id: ID du contenu Watchmode
        
        Returns:
            Dict: Détails du contenu
        """
        if not self.is_available:
            return {"error": "API key not available"}
        
        try:
            url = f"{self.base_url}/title/{content_id}/details/"
            params = {
                "apikey": self.api_key,
                "append_to_response": "sources"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_watchmode_details(data)
            
        except Exception as e:
            return {"error": f"Watchmode details error: {str(e)}"}
    
    def _format_watchmode_results(self, results: List[Dict]) -> List[Dict]:
        """Formate les résultats Watchmode dans un format standardisé."""
        formatted = []
        
        for item in results:
            media_type = "movie" if item.get("type") == "movie" else "tv"
            
            formatted_item = {
                "id": item.get("id"),
                "title": item.get("title"),
                "original_title": item.get("original_title", item.get("title")),
                "overview": item.get("plot_overview", ""),
                "poster_path": None,  # Watchmode ne fournit pas toujours les images
                "backdrop_path": None,
                "vote_average": item.get("imdb_rating", 0) / 10 if item.get("imdb_rating") else 0,
                "vote_count": 0,  # Watchmode ne fournit pas le nombre de votes
                "popularity": 0,
                "genre_ids": [],
                "genres": item.get("genre_names", []),
                "adult": False,
                "media_type": media_type,
                "release_date": item.get("year"),
                "provider": self.name,
                "watchmode_id": item.get("id"),
                "imdb_id": item.get("imdb_id"),
                "tmdb_id": item.get("tmdb_id")
            }
            formatted.append(formatted_item)
        
        return formatted
    
    def _format_watchmode_details(self, data: Dict) -> Dict:
        """Formate les détails Watchmode dans un format standardisé."""
        media_type = "movie" if data.get("type") == "movie" else "tv"
        
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "original_title": data.get("original_title", data.get("title")),
            "overview": data.get("plot_overview", ""),
            "poster_path": None,
            "backdrop_path": None,
            "vote_average": data.get("imdb_rating", 0) / 10 if data.get("imdb_rating") else 0,
            "vote_count": 0,
            "popularity": 0,
            "genres": data.get("genre_names", []),
            "runtime": data.get("runtime_minutes", 0),
            "release_date": data.get("year"),
            "status": "",
            "media_type": media_type,
            "production_companies": [],
            "media_type": media_type,
            "provider": self.name,
            "watchmode_id": data.get("id"),
            "imdb_id": data.get("imdb_id"),
            "tmdb_id": data.get("tmdb_id"),
            "sources": data.get("sources", [])  # Sources de streaming
        }

class MultiAPIManager:
    """Gestionnaire pour interroger plusieurs APIs simultanément."""
    
    def __init__(self):
        self.providers = [
            TMDbProvider(),
            WatchmodeProvider()
        ]
        self.available_providers = [p for p in self.providers if p.is_available]
    
    def search_content(self, query: str, content_type: str = "all", combine_results: bool = True) -> Dict:
        """
        Recherche de contenu sur tous les fournisseurs disponibles.
        
        Args:
            query: Terme de recherche
            content_type: Type de contenu à rechercher
            combine_results: Si True, combine les résultats de tous les fournisseurs
        
        Returns:
            Dict: Résultats combinés ou séparés par fournisseur
        """
        if not self.available_providers:
            return {"error": "No API providers available"}
        
        results = {}
        
        # Recherche parallèle sur tous les fournisseurs
        with ThreadPoolExecutor(max_workers=len(self.available_providers)) as executor:
            future_to_provider = {
                executor.submit(provider.search_content, query, content_type): provider
                for provider in self.available_providers
            }
            
            for future in as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    result = future.result(timeout=15)
                    results[provider.name] = result
                except Exception as e:
                    results[provider.name] = {
                        "results": [],
                        "provider": provider.name,
                        "error": f"Provider error: {str(e)}"
                    }
        
        if combine_results:
            return self._combine_search_results(results)
        else:
            return results
    
    def get_trending(self, media_type: str = "all", combine_results: bool = True) -> Dict:
        """
        Récupère le contenu tendance de tous les fournisseurs.
        
        Args:
            media_type: Type de contenu
            combine_results: Si True, combine les résultats
        
        Returns:
            Dict: Résultats combinés ou séparés
        """
        if not self.available_providers:
            return {"error": "No API providers available"}
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(self.available_providers)) as executor:
            future_to_provider = {
                executor.submit(provider.get_trending, media_type): provider
                for provider in self.available_providers
            }
            
            for future in as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    result = future.result(timeout=15)
                    results[provider.name] = result
                except Exception as e:
                    results[provider.name] = {
                        "results": [],
                        "provider": provider.name,
                        "error": f"Provider error: {str(e)}"
                    }
        
        if combine_results:
            return self._combine_trending_results(results)
        else:
            return results
    
    def _combine_search_results(self, results: Dict) -> Dict:
        """Combine les résultats de recherche de plusieurs fournisseurs."""
        combined_results = []
        total_results = 0
        errors = []
        
        for provider_name, provider_results in results.items():
            if "error" in provider_results:
                errors.append(f"{provider_name}: {provider_results['error']}")
                continue
            
            combined_results.extend(provider_results.get("results", []))
            total_results += provider_results.get("total_results", 0)
        
        # Déduplication basée sur le titre et l'année
        deduplicated = self._deduplicate_results(combined_results)
        
        # Tri par pertinence (vote_average * popularity)
        deduplicated.sort(
            key=lambda x: (x.get("vote_average", 0) * x.get("popularity", 1)), 
            reverse=True
        )
        
        return {
            "results": deduplicated,
            "total_results": len(deduplicated),
            "providers_used": list(results.keys()),
            "errors": errors if errors else None
        }
    
    def _combine_trending_results(self, results: Dict) -> Dict:
        """Combine les résultats tendance de plusieurs fournisseurs."""
        combined_results = []
        errors = []
        
        for provider_name, provider_results in results.items():
            if "error" in provider_results:
                errors.append(f"{provider_name}: {provider_results['error']}")
                continue
            
            combined_results.extend(provider_results.get("results", []))
        
        # Déduplication et tri
        deduplicated = self._deduplicate_results(combined_results)
        deduplicated.sort(
            key=lambda x: (x.get("vote_average", 0) * x.get("popularity", 1)), 
            reverse=True
        )
        
        return {
            "results": deduplicated[:50],  # Limiter à 50 résultats
            "providers_used": list(results.keys()),
            "errors": errors if errors else None
        }
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Supprime les doublons des résultats."""
        seen = set()
        deduplicated = []
        
        for item in results:
            # Créer une clé unique basée sur le titre et l'année
            title = item.get("title", "").lower().strip()
            year = str(item.get("release_date", ""))[:4]  # Prendre seulement l'année
            key = f"{title}_{year}_{item.get('media_type', '')}"
            
            if key not in seen and title:
                seen.add(key)
                deduplicated.append(item)
        
        return deduplicated
    
    def get_available_providers(self) -> List[str]:
        """Retourne la liste des fournisseurs disponibles."""
        return [p.name for p in self.available_providers]
    
    def test_all_providers(self) -> Dict:
        """Teste la connexion à tous les fournisseurs."""
        status = {}
        for provider in self.providers:
            status[provider.name] = {
                "available": provider.is_available,
                "connection": provider.test_connection() if provider.is_available else False
            }
        return status

# Instance globale du gestionnaire
api_manager = MultiAPIManager()
