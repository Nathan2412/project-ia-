"""
TMDb API Provider
Gère les requêtes vers l'API The Movie Database
"""

import requests
from typing import Dict, List, Optional, Any

class TMDbProvider:
    """Fournisseur pour l'API TMDb"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.name = "TMDb"
        
    def test_connection(self) -> bool:
        """Teste la connexion à l'API TMDb"""
        try:
            response = requests.get(
                f"{self.base_url}/configuration",
                params={"api_key": self.api_key},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Erreur de connexion TMDb: {e}")
            return False
    
    def search_content(self, query: str, content_type: str = "multi", page: int = 1) -> Dict[str, Any]:
        """
        Recherche de contenu sur TMDb
        
        Args:
            query: Terme de recherche
            content_type: Type de contenu ('movie', 'tv', 'multi')
            page: Numéro de page
            
        Returns:
            Résultats de recherche formatés
        """
        endpoint = f"{self.base_url}/search/{content_type}"
        params = {
            "api_key": self.api_key,
            "language": "fr-FR",
            "query": query,
            "page": page,
            "include_adult": False
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("results", []):
                    formatted_item = self._format_search_result(item)
                    if formatted_item:
                        results.append(formatted_item)
                
                return {
                    "results": results,
                    "total_results": data.get("total_results", 0),
                    "total_pages": data.get("total_pages", 0),
                    "current_page": page
                }
            else:
                return {"error": f"Erreur TMDb: {response.status_code}"}
        except Exception as e:
            return {"error": f"Exception TMDb: {str(e)}"}
    
    def get_trending(self, content_type: str = "all", time_window: str = "week") -> Dict[str, Any]:
        """
        Récupère le contenu tendance de TMDb
        
        Args:
            content_type: Type de contenu ('movie', 'tv', 'all')
            time_window: Période ('day', 'week')
            
        Returns:
            Contenu tendance formaté
        """
        endpoint = f"{self.base_url}/trending/{content_type}/{time_window}"
        params = {
            "api_key": self.api_key,
            "language": "fr-FR"
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("results", []):
                    formatted_item = self._format_search_result(item)
                    if formatted_item:
                        results.append(formatted_item)
                
                return {"results": results}
            else:
                return {"error": f"Erreur TMDb trending: {response.status_code}"}
        except Exception as e:
            return {"error": f"Exception TMDb trending: {str(e)}"}
    
    def get_details(self, item_id: int, content_type: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un élément
        
        Args:
            item_id: ID de l'élément
            content_type: Type ('movie' ou 'tv')
            
        Returns:
            Détails de l'élément
        """
        endpoint = f"{self.base_url}/{content_type}/{item_id}"
        params = {
            "api_key": self.api_key,
            "language": "fr-FR",
            "append_to_response": "credits,keywords,watch/providers"
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Erreur détails TMDb: {response.status_code}"}
        except Exception as e:
            return {"error": f"Exception détails TMDb: {str(e)}"}
    
    def get_genre_list(self, content_type: str = "movie") -> Dict[int, str]:
        """Récupère la liste des genres"""
        endpoint = f"{self.base_url}/genre/{content_type}/list"
        params = {
            "api_key": self.api_key,
            "language": "fr-FR"
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                genres = response.json().get("genres", [])
                return {genre["id"]: genre["name"] for genre in genres}
            return {}
        except Exception as e:
            print(f"Erreur récupération genres TMDb: {e}")
            return {}
    
    def discover_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """
        Découverte de contenu avec filtres avancés
        
        Args:
            content_type: Type de contenu ('movie' ou 'tv')
            **kwargs: Paramètres de filtre
            
        Returns:
            Résultats de découverte
        """
        endpoint = f"{self.base_url}/discover/{content_type}"
        params = {
            "api_key": self.api_key,
            "language": "fr-FR",
            **kwargs
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("results", []):
                    formatted_item = self._format_search_result(item)
                    if formatted_item:
                        results.append(formatted_item)
                
                return {"results": results}
            else:
                return {"error": f"Erreur découverte TMDb: {response.status_code}"}
        except Exception as e:
            return {"error": f"Exception découverte TMDb: {str(e)}"}
    
    def _format_search_result(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Formate un résultat de recherche TMDb"""
        try:
            # Déterminer le type de média
            media_type = item.get("media_type")
            if not media_type:
                if "title" in item:
                    media_type = "movie"
                elif "name" in item:
                    media_type = "tv"
                else:
                    return None
            
            # Titre et date
            title = item.get("title") or item.get("name", "Sans titre")
            release_date = item.get("release_date") or item.get("first_air_date", "")
            year = release_date[:4] if release_date else ""
            
            return {
                "id": item.get("id"),
                "title": title,
                "year": year,
                "rating": item.get("vote_average", 0),
                "description": item.get("overview", "Pas de description disponible"),
                "poster_path": item.get("poster_path"),
                "backdrop_path": item.get("backdrop_path"),
                "genre_ids": item.get("genre_ids", []),
                "popularity": item.get("popularity", 0),
                "vote_count": item.get("vote_count", 0),
                "media_type": media_type,
                "provider": "TMDb"
            }
        except Exception as e:
            print(f"Erreur formatage résultat TMDb: {e}")
            return None
