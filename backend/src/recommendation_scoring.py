"""
Module de scoring et recommandations
Algorithmes avancés pour calculer la pertinence des recommandations
"""

from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import math

class RecommendationScorer:
    """Classe pour calculer les scores de recommandation"""
    
    def __init__(self, genre_weights: Dict[str, float] = None):
        # Poids par défaut pour différents facteurs
        self.weights = {
            "rating": 0.25,
            "popularity": 0.15,
            "genre_match": 0.30,
            "keyword_match": 0.15,
            "director_match": 0.10,
            "streaming_availability": 0.05
        }
        
        # Mapping des genres avec leurs poids de qualité
        self.genre_quality_weights = genre_weights or {
            "Drama": 1.2,
            "Thriller": 1.1,
            "Science Fiction": 1.1,
            "Mystery": 1.1,
            "Crime": 1.0,
            "Action": 0.9,
            "Comedy": 0.9,
            "Horror": 0.8,
            "Romance": 0.8,
            "Animation": 1.0
        }
    
    def calculate_item_score(self, item: Dict[str, Any], user_preferences: Dict[str, Any], 
                           detailed_info: Dict[str, Any] = None) -> float:
        """
        Calcule le score de recommandation pour un élément
        
        Args:
            item: Élément à scorer
            user_preferences: Préférences utilisateur
            detailed_info: Informations détaillées de l'élément (optionnel)
            
        Returns:
            Score de recommandation
        """
        score = 0.0
        
        try:
            # Score de base (rating et popularité)
            score += self._calculate_base_score(item, user_preferences)
            
            # Score des genres
            score += self._calculate_genre_score(item, user_preferences, detailed_info)
            
            # Score des mots-clés
            score += self._calculate_keyword_score(item, user_preferences, detailed_info)
            
            # Score des réalisateurs/créateurs
            score += self._calculate_director_score(item, user_preferences, detailed_info)
            
            # Score de disponibilité streaming
            score += self._calculate_streaming_score(item, user_preferences, detailed_info)
            
            # Pénalités et bonus
            score = self._apply_penalties_and_bonuses(score, item, user_preferences, detailed_info)
            
        except Exception as e:
            print(f"Erreur calcul score: {e}")
            return 0.0
        
        return max(0.0, score)  # Score minimum de 0
    
    def _calculate_base_score(self, item: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        """Calcule le score de base (rating + popularité)"""
        score = 0.0
        
        # Score basé sur la note
        rating = item.get("rating", 0)
        min_rating = user_preferences.get("rating_min", 7.0)
        
        if rating >= min_rating:
            # Bonus pour dépassement du minimum
            rating_score = (rating - min_rating) * 2 + rating * 0.5
            score += rating_score * self.weights["rating"]
        else:
            # Pénalité pour note insuffisante
            score -= (min_rating - rating) * 0.5
        
        # Score basé sur la popularité (normalisé)
        popularity = item.get("popularity", 0)
        if popularity > 0:
            # Logarithme pour éviter que les films très populaires dominent
            popularity_score = math.log10(popularity + 1) * 2
            score += min(popularity_score, 5) * self.weights["popularity"]
        
        return score
    
    def _calculate_genre_score(self, item: Dict[str, Any], user_preferences: Dict[str, Any], 
                             detailed_info: Dict[str, Any] = None) -> float:
        """Calcule le score basé sur les genres"""
        score = 0.0
        
        user_likes = [g.lower() for g in user_preferences.get("genres_likes", [])]
        user_dislikes = [g.lower() for g in user_preferences.get("genres_dislikes", [])]
        
        # Récupérer les genres de l'élément
        item_genres = []
        
        # Depuis les informations détaillées (TMDb)
        if detailed_info and "genres" in detailed_info:
            item_genres = [g["name"].lower() for g in detailed_info["genres"]]
        # Depuis les noms de genres (Watchmode)
        elif "genre_names" in item:
            item_genres = [g.lower() for g in item["genre_names"]]
        # Fallback depuis les IDs de genres
        elif "genre_ids" in item:
            # Conversion basique des IDs courants
            genre_map = {
                28: "action", 18: "drama", 35: "comedy", 80: "crime",
                99: "documentary", 878: "science fiction", 53: "thriller"
            }
            item_genres = [genre_map.get(gid, "").lower() for gid in item["genre_ids"]]
            item_genres = [g for g in item_genres if g]
        
        if not item_genres:
            return score
        
        # Calculer les correspondances
        matching_genres = 0
        disliked_genres = 0
        quality_bonus = 0
        
        for genre in item_genres:
            # Genres aimés
            for liked in user_likes:
                if liked in genre or genre in liked:
                    matching_genres += 1
                    score += 3.0
                    
                    # Bonus qualité pour certains genres
                    quality_bonus += self.genre_quality_weights.get(genre.title(), 1.0) * 0.5
                    break
            
            # Genres non aimés
            for disliked in user_dislikes:
                if disliked in genre or genre in disliked:
                    disliked_genres += 1
                    score -= 4.0
                    break
        
        # Bonus pour correspondance multiple
        if matching_genres > 1:
            score += matching_genres * 0.5
        
        # Bonus qualité
        score += quality_bonus
        
        # Pénalité si aucun genre aimé
        if user_likes and matching_genres == 0:
            score -= 2.0
        
        return score * self.weights["genre_match"]
    
    def _calculate_keyword_score(self, item: Dict[str, Any], user_preferences: Dict[str, Any], 
                               detailed_info: Dict[str, Any] = None) -> float:
        """Calcule le score basé sur les mots-clés"""
        score = 0.0
        
        user_keywords = [k.lower() for k in user_preferences.get("keywords_likes", [])]
        if not user_keywords:
            return score
        
        # Mots-clés dans la description
        description = item.get("description", "").lower()
        matched_keywords = 0
        
        for keyword in user_keywords:
            if keyword in description:
                score += 2.0
                matched_keywords += 1
        
        # Mots-clés TMDb (si disponibles)
        if detailed_info and "keywords" in detailed_info:
            tmdb_keywords = detailed_info["keywords"].get("keywords", [])
            for tmdb_keyword in tmdb_keywords:
                keyword_name = tmdb_keyword.get("name", "").lower()
                for user_keyword in user_keywords:
                    if user_keyword in keyword_name or keyword_name in user_keyword:
                        score += 2.5
                        matched_keywords += 1
                        break
        
        # Bonus pour correspondances multiples
        if matched_keywords > 1:
            score += matched_keywords * 0.3
        
        return score * self.weights["keyword_match"]
    
    def _calculate_director_score(self, item: Dict[str, Any], user_preferences: Dict[str, Any], 
                                detailed_info: Dict[str, Any] = None) -> float:
        """Calcule le score basé sur les réalisateurs/créateurs"""
        score = 0.0
        
        user_directors = [d.lower() for d in user_preferences.get("directors_likes", [])]
        if not user_directors:
            return score
        
        # Vérifier dans les informations détaillées
        if detailed_info and "credits" in detailed_info:
            # Pour les films
            if "crew" in detailed_info["credits"]:
                directors = [
                    person["name"].lower() 
                    for person in detailed_info["credits"]["crew"] 
                    if person["job"] == "Director"
                ]
                
                for director in directors:
                    for user_director in user_directors:
                        if user_director in director or director in user_director:
                            score += 5.0  # Fort bonus pour réalisateur préféré
                            break
            
            # Pour les séries (créateurs)
            if "created_by" in detailed_info:
                creators = [person["name"].lower() for person in detailed_info["created_by"]]
                for creator in creators:
                    for user_director in user_directors:
                        if user_director in creator or creator in user_director:
                            score += 5.0
                            break
        
        return score * self.weights["director_match"]
    
    def _calculate_streaming_score(self, item: Dict[str, Any], user_preferences: Dict[str, Any], 
                                 detailed_info: Dict[str, Any] = None) -> float:
        """Calcule le score de disponibilité streaming"""
        score = 0.0
        
        user_services = user_preferences.get("streaming_services", [])
        if not user_services:
            return score
        
        # Services disponibles pour l'élément
        available_services = []
        
        # Depuis les informations de streaming
        if "streaming_services" in item:
            available_services = item["streaming_services"]
        elif detailed_info and "enhanced_streaming" in detailed_info:
            available_services = detailed_info["enhanced_streaming"].get("streaming_services", [])
        elif detailed_info and "watch/providers" in detailed_info:
            # Parser les providers TMDb
            providers_fr = detailed_info["watch/providers"].get("results", {}).get("FR", {})
            if "flatrate" in providers_fr:
                for provider in providers_fr["flatrate"]:
                    provider_name = provider.get("provider_name", "").lower()
                    if "netflix" in provider_name:
                        available_services.append("netflix")
                    elif "disney" in provider_name:
                        available_services.append("disney")
                    elif "amazon" in provider_name or "prime" in provider_name:
                        available_services.append("amazon")
        
        # Calculer le score
        matching_services = sum(1 for service in user_services if service in available_services)
        if matching_services > 0:
            score += matching_services * 2.0
        
        return score * self.weights["streaming_availability"]
    
    def _apply_penalties_and_bonuses(self, score: float, item: Dict[str, Any], 
                                   user_preferences: Dict[str, Any], 
                                   detailed_info: Dict[str, Any] = None) -> float:
        """Applique les pénalités et bonus finaux"""
        
        # Bonus pour films récents (si préférence)
        year = item.get("year", "")
        if year and len(year) >= 4:
            try:
                item_year = int(year[:4])
                current_year = 2025  # Année actuelle
                
                # Bonus pour contenu récent (5 dernières années)
                if current_year - item_year <= 5:
                    score += 1.0
                # Pénalité légère pour contenu très ancien (plus de 20 ans)
                elif current_year - item_year > 20:
                    score -= 0.5
                    
            except ValueError:
                pass
        
        # Bonus pour vote count élevé (plus fiable)
        vote_count = item.get("vote_count", 0)
        if vote_count > 1000:
            score += 1.0
        elif vote_count > 500:
            score += 0.5
        elif vote_count < 50:
            score -= 1.0  # Pénalité pour peu d'évaluations
        
        # Pénalité pour éléments déjà vus
        item_id = str(item.get("id", ""))
        user_history = [str(h) for h in user_preferences.get("history", [])]
        if item_id in user_history:
            score -= 10.0  # Forte pénalité pour éviter les doublons
        
        return score

class RecommendationEngine:
    """Moteur de recommandation principal"""
    
    def __init__(self, api_manager, scorer: RecommendationScorer = None):
        self.api_manager = api_manager
        self.scorer = scorer or RecommendationScorer()
    
    def get_personalized_recommendations(self, user_preferences: Dict[str, Any], 
                                       content_type: str = "all", 
                                       max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Génère des recommandations personnalisées
        
        Args:
            user_preferences: Préférences utilisateur
            content_type: Type de contenu
            max_results: Nombre de recommandations
            
        Returns:
            Liste de recommandations scorées
        """
        recommendations = []
        
        try:
            # 1. Recherche basée sur les genres préférés
            genre_results = self._search_by_genres(user_preferences, content_type)
            
            # 2. Recherche basée sur les mots-clés
            keyword_results = self._search_by_keywords(user_preferences, content_type)
            
            # 3. Contenu tendance filtré
            trending_results = self._get_filtered_trending(user_preferences, content_type)
            
            # 4. Combiner tous les résultats
            all_candidates = genre_results + keyword_results + trending_results
            
            # 5. Déduplication
            unique_candidates = self._deduplicate_results(all_candidates)
            
            # 6. Scoring parallèle
            recommendations = self._score_candidates_parallel(unique_candidates, user_preferences)
            
            # 7. Tri et sélection finale
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            print(f"Erreur génération recommandations: {e}")
        
        return recommendations[:max_results]
    
    def _search_by_genres(self, user_preferences: Dict[str, Any], 
                         content_type: str) -> List[Dict[str, Any]]:
        """Recherche basée sur les genres préférés"""
        results = []
        genres_likes = user_preferences.get("genres_likes", [])
        
        for genre in genres_likes[:3]:  # Limiter à 3 genres pour éviter trop de requêtes
            try:
                search_results = self.api_manager.search_content_parallel(
                    query=genre, 
                    content_type=content_type, 
                    max_results=10
                )
                
                if not search_results.get("error"):
                    results.extend(search_results.get("results", []))
                    
            except Exception as e:
                print(f"Erreur recherche genre {genre}: {e}")
        
        return results
    
    def _search_by_keywords(self, user_preferences: Dict[str, Any], 
                           content_type: str) -> List[Dict[str, Any]]:
        """Recherche basée sur les mots-clés"""
        results = []
        keywords = user_preferences.get("keywords_likes", [])
        
        for keyword in keywords[:2]:  # Limiter à 2 mots-clés
            try:
                search_results = self.api_manager.search_content_parallel(
                    query=keyword, 
                    content_type=content_type, 
                    max_results=8
                )
                
                if not search_results.get("error"):
                    results.extend(search_results.get("results", []))
                    
            except Exception as e:
                print(f"Erreur recherche mot-clé {keyword}: {e}")
        
        return results
    
    def _get_filtered_trending(self, user_preferences: Dict[str, Any], 
                              content_type: str) -> List[Dict[str, Any]]:
        """Récupère le contenu tendance filtré"""
        try:
            trending_results = self.api_manager.get_trending_parallel(
                content_type=content_type, 
                max_results=15
            )
            
            if not trending_results.get("error"):
                return trending_results.get("results", [])
                
        except Exception as e:
            print(f"Erreur récupération tendances: {e}")
        
        return []
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Supprime les doublons"""
        seen = set()
        unique_results = []
        
        for item in results:
            # Clé unique basée sur titre + année + type
            key = f"{item.get('title', '').lower()}_{item.get('year', '')}_{item.get('media_type', '')}"
            
            if key not in seen:
                seen.add(key)
                unique_results.append(item)
        
        return unique_results
    
    def _score_candidates_parallel(self, candidates: List[Dict[str, Any]], 
                                 user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score les candidats en parallèle"""
        recommendations = []
        
        def score_item(item):
            try:
                # Récupérer les détails si possible
                detailed_info = None
                if item.get("provider") == "TMDb" and item.get("id"):
                    detailed_info = self.api_manager.get_enhanced_details(
                        item["id"], 
                        item.get("media_type", "movie")
                    )
                
                # Calculer le score
                score = self.scorer.calculate_item_score(item, user_preferences, detailed_info)
                
                return {
                    "item": item,
                    "score": score,
                    "type": "movie" if item.get("media_type") == "movie" else "series",
                    "detailed_info": detailed_info
                }
                
            except Exception as e:
                print(f"Erreur scoring item {item.get('title', 'Unknown')}: {e}")
                return None
        
        # Exécution parallèle du scoring
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(score_item, candidates))
        
        # Filtrer les résultats None
        recommendations = [r for r in results if r and r["score"] > 0]
        
        return recommendations
