"""
Utilitaires pour les recommandations
Fonctions helper et outils communs
"""

import json
import hashlib
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class CacheManager:
    """Gestionnaire de cache pour les requêtes API"""
    
    def __init__(self, cache_duration_minutes: int = 60):
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
    
    def get_cache_key(self, *args) -> str:
        """Génère une clé de cache basée sur les arguments"""
        key_string = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache si elle est valide"""
        if key in self.cache:
            cached_item = self.cache[key]
            if datetime.now() - cached_item["timestamp"] < self.cache_duration:
                return cached_item["data"]
            else:
                # Supprimer l'entrée expirée
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Any):
        """Stocke une valeur dans le cache"""
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    def clear_expired(self):
        """Nettoie les entrées expirées du cache"""
        current_time = datetime.now()
        expired_keys = [
            key for key, item in self.cache.items()
            if current_time - item["timestamp"] >= self.cache_duration
        ]
        
        for key in expired_keys:
            del self.cache[key]

class StreamingServiceMapper:
    """Mapper pour normaliser les noms des services de streaming"""
    
    # Mapping des noms de services vers des identifiants normalisés
    SERVICE_MAPPING = {
        # Netflix variations
        "netflix": "netflix",
        "netflix france": "netflix",
        "netflix fr": "netflix",
        
        # Disney+ variations
        "disney+": "disney",
        "disney plus": "disney", 
        "disney+ france": "disney",
        "walt disney pictures": "disney",
        
        # Amazon Prime variations
        "amazon prime video": "amazon",
        "amazon prime": "amazon",
        "prime video": "amazon",
        "amazon": "amazon",
        
        # HBO variations
        "hbo max": "hbo",
        "hbo": "hbo",
        "hbo france": "hbo",
        
        # Apple TV+ variations
        "apple tv+": "apple",
        "apple tv plus": "apple",
        "apple": "apple",
        
        # Paramount+ variations
        "paramount+": "paramount",
        "paramount plus": "paramount",
        "paramount": "paramount",
        
        # Autres services
        "hulu": "hulu",
        "peacock": "peacock"
    }
    
    @classmethod
    def normalize_service_name(cls, service_name: str) -> str:
        """Normalise le nom d'un service de streaming"""
        if not service_name:
            return ""
        
        normalized = service_name.lower().strip()
        return cls.SERVICE_MAPPING.get(normalized, normalized)
    
    @classmethod
    def get_supported_services(cls) -> List[str]:
        """Retourne la liste des services supportés"""
        return list(set(cls.SERVICE_MAPPING.values()))

class ContentTypeConverter:
    """Convertisseur pour les types de contenu entre différentes APIs"""
    
    # Mapping des types entre notre système et les APIs
    TYPE_MAPPINGS = {
        "internal_to_tmdb": {
            "movies": "movie",
            "series": "tv",
            "all": "multi"
        },
        "internal_to_watchmode": {
            "movies": "movie",
            "series": "tv_series",
            "all": ""
        },
        "tmdb_to_internal": {
            "movie": "movies",
            "tv": "series",
            "multi": "all"
        },
        "watchmode_to_internal": {
            "movie": "movies",
            "tv_series": "series"
        }
    }
    
    @classmethod
    def convert_type(cls, content_type: str, from_system: str, to_system: str) -> str:
        """
        Convertit un type de contenu entre systèmes
        
        Args:
            content_type: Type à convertir
            from_system: Système source (internal, tmdb, watchmode)
            to_system: Système cible (internal, tmdb, watchmode)
            
        Returns:
            Type converti
        """
        mapping_key = f"{from_system}_to_{to_system}"
        
        if mapping_key in cls.TYPE_MAPPINGS:
            return cls.TYPE_MAPPINGS[mapping_key].get(content_type, content_type)
        
        return content_type

class GenreManager:
    """Gestionnaire pour les genres et leur mapping"""
    
    # Genres standards avec leurs variations
    GENRE_VARIATIONS = {
        "action": ["action", "adventure", "aventure"],
        "comedy": ["comedy", "comédie", "comedie"],
        "drama": ["drama", "drame"],
        "horror": ["horror", "horreur", "épouvante"],
        "thriller": ["thriller", "suspense"],
        "romance": ["romance", "romantique"],
        "science_fiction": ["science fiction", "sci-fi", "science-fiction", "sf"],
        "fantasy": ["fantasy", "fantastique", "fantaisie"],
        "animation": ["animation", "anime", "animé"],
        "documentary": ["documentary", "documentaire"],
        "crime": ["crime", "criminel", "polar"],
        "mystery": ["mystery", "mystère", "mystere"],
        "war": ["war", "guerre"],
        "western": ["western"],
        "music": ["music", "musical", "musique"],
        "family": ["family", "famille", "familial"],
        "biography": ["biography", "biographie", "biopic"]
    }
    
    @classmethod
    def normalize_genre(cls, genre: str) -> Optional[str]:
        """Normalise un nom de genre"""
        if not genre:
            return None
        
        genre_lower = genre.lower().strip()
        
        for standard_genre, variations in cls.GENRE_VARIATIONS.items():
            if genre_lower in variations:
                return standard_genre
        
        return genre_lower
    
    @classmethod
    def get_genre_variations(cls, genre: str) -> List[str]:
        """Retourne toutes les variations d'un genre"""
        normalized = cls.normalize_genre(genre)
        if normalized and normalized in cls.GENRE_VARIATIONS:
            return cls.GENRE_VARIATIONS[normalized]
        return [genre] if genre else []

class RecommendationFormatter:
    """Formateur pour les recommandations finales"""
    
    @staticmethod
    def format_recommendation(recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate une recommandation pour l'API frontend
        
        Args:
            recommendation: Recommandation brute
            
        Returns:
            Recommandation formatée
        """
        item = recommendation.get("item", {})
        detailed_info = recommendation.get("detailed_info", {})
        
        # Informations de base
        formatted = {
            "id": item.get("id"),
            "title": item.get("title", "Sans titre"),
            "year": item.get("year", ""),
            "rating": round(item.get("rating", 0), 1),
            "description": item.get("description", "Pas de description disponible"),
            "type": recommendation.get("type", "movie"),
            "score": round(recommendation.get("score", 0), 2),
            "provider": item.get("provider", "Unknown")
        }
        
        # Images
        if item.get("poster_path"):
            formatted["poster_url"] = f"https://image.tmdb.org/t/p/w500{item['poster_path']}"
        
        if item.get("backdrop_path"):
            formatted["backdrop_url"] = f"https://image.tmdb.org/t/p/w1280{item['backdrop_path']}"
        
        # Genres
        if detailed_info and "genres" in detailed_info:
            formatted["genres"] = [g["name"] for g in detailed_info["genres"]]
        elif "genre_names" in item:
            formatted["genres"] = item["genre_names"]
        else:
            formatted["genres"] = []
        
        # Réalisateur/Créateur
        if detailed_info and "credits" in detailed_info:
            if "crew" in detailed_info["credits"]:
                directors = [
                    person["name"] for person in detailed_info["credits"]["crew"]
                    if person["job"] == "Director"
                ]
                if directors:
                    formatted["director"] = directors[0]  # Premier réalisateur
        
        # Créateurs pour les séries
        if detailed_info and "created_by" in detailed_info:
            creators = [person["name"] for person in detailed_info["created_by"]]
            if creators:
                formatted["creator"] = creators[0]
        
        # Services de streaming
        streaming_services = []
        
        # Depuis les informations enrichies
        if detailed_info and "enhanced_streaming" in detailed_info:
            streaming_services = detailed_info["enhanced_streaming"].get("streaming_services", [])
        
        # Depuis les informations TMDb
        elif detailed_info and "watch/providers" in detailed_info:
            providers_fr = detailed_info["watch/providers"].get("results", {}).get("FR", {})
            if "flatrate" in providers_fr:
                for provider in providers_fr["flatrate"]:
                    service = StreamingServiceMapper.normalize_service_name(
                        provider.get("provider_name", "")
                    )
                    if service and service not in streaming_services:
                        streaming_services.append(service)
        
        # Depuis l'item directement
        elif "streaming_services" in item:
            streaming_services = item["streaming_services"]
        
        formatted["streaming_services"] = streaming_services
        
        # Métadonnées supplémentaires
        formatted["metadata"] = {
            "vote_count": item.get("vote_count", 0),
            "popularity": item.get("popularity", 0),
            "tmdb_id": item.get("id") if item.get("provider") == "TMDb" else item.get("tmdb_id"),
            "watchmode_id": item.get("watchmode_id"),
            "imdb_id": item.get("imdb_id")
        }
        
        return formatted
    
    @staticmethod
    def format_recommendation_list(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Formate une liste de recommandations"""
        return [
            RecommendationFormatter.format_recommendation(rec) 
            for rec in recommendations
        ]

class PerformanceMonitor:
    """Moniteur de performance pour les requêtes API"""
    
    def __init__(self):
        self.metrics = {
            "api_calls": 0,
            "total_response_time": 0,
            "errors": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def record_api_call(self, response_time: float, success: bool = True):
        """Enregistre une requête API"""
        self.metrics["api_calls"] += 1
        self.metrics["total_response_time"] += response_time
        
        if not success:
            self.metrics["errors"] += 1
    
    def record_cache_hit(self):
        """Enregistre un hit de cache"""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Enregistre une miss de cache"""
        self.metrics["cache_misses"] += 1
    
    def get_average_response_time(self) -> float:
        """Calcule le temps de réponse moyen"""
        if self.metrics["api_calls"] > 0:
            return self.metrics["total_response_time"] / self.metrics["api_calls"]
        return 0.0
    
    def get_error_rate(self) -> float:
        """Calcule le taux d'erreur"""
        if self.metrics["api_calls"] > 0:
            return self.metrics["errors"] / self.metrics["api_calls"]
        return 0.0
    
    def get_cache_hit_rate(self) -> float:
        """Calcule le taux de hit de cache"""
        total_cache_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total_cache_requests > 0:
            return self.metrics["cache_hits"] / total_cache_requests
        return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne toutes les statistiques"""
        return {
            **self.metrics,
            "average_response_time": self.get_average_response_time(),
            "error_rate": self.get_error_rate(),
            "cache_hit_rate": self.get_cache_hit_rate()
        }
    
    def reset(self):
        """Remet à zéro toutes les métriques"""
        for key in self.metrics:
            self.metrics[key] = 0
