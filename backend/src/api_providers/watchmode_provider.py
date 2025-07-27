"""
Watchmode API Provider via RapidAPI
Gère les requêtes vers l'API Watchmode pour enrichir les données de films et séries
"""

import requests
from typing import Dict, List, Optional, Any

class WatchmodeProvider:
    """Fournisseur pour l'API Watchmode directe"""
    
    def __init__(self, api_key: str, use_rapidapi: bool = False):
        self.api_key = api_key
        self.name = "Watchmode"
        
        if use_rapidapi:
            # Configuration RapidAPI
            self.base_url = "https://watchmode.p.rapidapi.com"
            self.headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "watchmode.p.rapidapi.com"
            }
        else:
            # Configuration API directe
            self.base_url = "https://api.watchmode.com/v1"
            self.headers = {}
        
    def test_connection(self) -> bool:
        """Teste la connexion à l'API Watchmode"""
        try:
            if "rapidapi" in self.base_url:
                # Test RapidAPI
                response = requests.get(
                    f"{self.base_url}/regions/",
                    headers=self.headers,
                    timeout=5
                )
            else:
                # Test API directe
                response = requests.get(
                    f"{self.base_url}/regions/?apikey={self.api_key}",
                    headers=self.headers,
                    timeout=5
                )
            return response.status_code == 200
        except Exception as e:
            print(f"Erreur de connexion Watchmode: {e}")
            return False
    
    def search_content(self, query: str, content_type: str = "all", page: int = 1) -> Dict[str, Any]:
        """
        Recherche de contenu sur Watchmode
        
        Args:
            query: Terme de recherche
            content_type: Type de contenu ('movie', 'tv', 'all')
            page: Numéro de page
            
        Returns:
            Résultats de recherche formatés
        """
        endpoint = f"{self.base_url}/search/"
        
        # Convertir les types de contenu
        type_mapping = {
            "movie": "movie",
            "tv": "tv_series",
            "all": ""
        }
        watchmode_type = type_mapping.get(content_type, "")
        
        params = {
            "search_field": "name",
            "search_value": query,
            "page": page
        }
        
        if watchmode_type:
            params["types"] = watchmode_type
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("title_results", []):
                    formatted_item = self._format_search_result(item)
                    if formatted_item:
                        results.append(formatted_item)
                
                return {
                    "results": results,
                    "total_results": len(results),
                    "current_page": page
                }
            else:
                return {"error": f"Erreur Watchmode: {response.status_code}"}
        except Exception as e:
            return {"error": f"Exception Watchmode: {str(e)}"}
    
    def get_trending(self, content_type: str = "all") -> Dict[str, Any]:
        """
        Récupère le contenu populaire de Watchmode
        
        Args:
            content_type: Type de contenu ('movie', 'tv', 'all')
            
        Returns:
            Contenu populaire formaté
        """
        endpoint = f"{self.base_url}/list-titles/"
        
        # Convertir les types de contenu
        type_mapping = {
            "movie": "movie",
            "tv": "tv_series",
            "all": ""
        }
        watchmode_type = type_mapping.get(content_type, "")
        
        params = {
            "page": 1,
            "sort_by": "popularity_desc"
        }
        
        if watchmode_type:
            params["types"] = watchmode_type
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("titles", []):
                    formatted_item = self._format_search_result(item)
                    if formatted_item:
                        results.append(formatted_item)
                
                return {"results": results[:20]}  # Limiter à 20 résultats
            else:
                return {"error": f"Erreur Watchmode trending: {response.status_code}"}
        except Exception as e:
            return {"error": f"Exception Watchmode trending: {str(e)}"}
    
    def get_details(self, item_id: int) -> Dict[str, Any]:
        """
        Récupère les détails d'un élément Watchmode
        
        Args:
            item_id: ID Watchmode de l'élément
            
        Returns:
            Détails de l'élément
        """
        endpoint = f"{self.base_url}/title/{item_id}/details/"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Erreur détails Watchmode: {response.status_code}"}
        except Exception as e:
            return {"error": f"Exception détails Watchmode: {str(e)}"}
    
    def get_streaming_sources(self, item_id: int, region: str = "FR") -> Dict[str, Any]:
        """
        Récupère les sources de streaming pour un élément
        
        Args:
            item_id: ID Watchmode de l'élément
            region: Code région (FR, US, etc.)
            
        Returns:
            Sources de streaming disponibles
        """
        endpoint = f"{self.base_url}/title/{item_id}/sources/"
        params = {"regions": region}
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._format_streaming_sources(data)
            else:
                return {"error": f"Erreur sources Watchmode: {response.status_code}"}
        except Exception as e:
            return {"error": f"Exception sources Watchmode: {str(e)}"}
    
    def get_genres(self) -> Dict[str, Any]:
        """Récupère la liste des genres Watchmode"""
        endpoint = f"{self.base_url}/genres/"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Erreur récupération genres Watchmode: {e}")
            return {}
    
    def _format_search_result(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Formate un résultat de recherche Watchmode"""
        try:
            # Déterminer le type de média
            item_type = item.get("type", "")
            if item_type == "movie":
                media_type = "movie"
            elif item_type == "tv_series":
                media_type = "tv"
            else:
                media_type = "movie"  # Par défaut
            
            # Titre et année
            title = item.get("name", "Sans titre")
            year = str(item.get("year", "")) if item.get("year") else ""
            
            # Note (Watchmode utilise une échelle différente)
            user_rating = item.get("user_rating", 0)
            # Convertir l'échelle Watchmode (0-10) vers TMDb (0-10)
            rating = float(user_rating) if user_rating else 0
            
            return {
                "id": item.get("id"),
                "title": title,
                "year": year,
                "rating": rating,
                "description": item.get("plot_overview", "Pas de description disponible"),
                "poster_path": None,  # Watchmode n'a pas toujours les posters
                "backdrop_path": None,
                "genre_names": item.get("genre_names", []),
                "popularity": item.get("relevance_percentile", 0),
                "vote_count": 0,  # Pas disponible dans Watchmode
                "media_type": media_type,
                "provider": "Watchmode",
                "watchmode_id": item.get("id"),
                "imdb_id": item.get("imdb_id"),
                "tmdb_id": item.get("tmdb_id")
            }
        except Exception as e:
            print(f"Erreur formatage résultat Watchmode: {e}")
            return None
    
    def _format_streaming_sources(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les sources de streaming"""
        try:
            sources = {}
            for source in data.get("sources", []):
                source_name = source.get("name", "").lower()
                source_type = source.get("type", "")
                
                if source_type == "subscription":
                    # Mapper les noms de services
                    if "netflix" in source_name:
                        sources["netflix"] = True
                    elif "disney" in source_name or "disney+" in source_name:
                        sources["disney"] = True
                    elif "amazon" in source_name or "prime" in source_name:
                        sources["amazon"] = True
                    elif "hbo" in source_name:
                        sources["hbo"] = True
                    elif "hulu" in source_name:
                        sources["hulu"] = True
                    elif "apple" in source_name:
                        sources["apple"] = True
                    elif "paramount" in source_name:
                        sources["paramount"] = True
            
            return {"streaming_services": list(sources.keys())}
        except Exception as e:
            print(f"Erreur formatage sources streaming: {e}")
            return {"streaming_services": []}
