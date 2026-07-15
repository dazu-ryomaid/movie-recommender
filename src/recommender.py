#!/usr/bin/env python3
"""
Algorithmes de recommandation pour le système de recommandation de films.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from src.database import Database
from src.models import Movie, Rating, Recommendation


class RecommenderSystem:
    """Classe pour générer des recommandations de films."""
    
    def __init__(self, db: Database):
        self.db = db
        self._cache = {}  # Cache pour les calculs coûteux
    
    def get_content_based_recommendations(
        self, user_id: int, limit: int = 5
    ) -> List[Recommendation]:
        """
        Génère des recommandations basées sur le contenu (genres des films notés).
        """
        # Récupérer les films notés par l'utilisateur
        ratings = self.db.get_ratings_by_user(user_id)
        if not ratings:
            # Si l'utilisateur n'a pas noté de films, recommander des films populaires
            return self.get_popular_recommendations(limit)
        
        # Récupérer les genres des films notés
        user_genres = {}
        for rating in ratings:
            movie = self.db.get_movie_by_id(rating.movie_id)
            if movie and movie.genres:
                for genre in movie.genres:
                    user_genres[genre] = user_genres.get(genre, 0) + rating.rating
        
        if not user_genres:
            return self.get_popular_recommendations(limit)
        
        # Normaliser les poids des genres
        total = sum(user_genres.values())
        user_genres = {g: w / total for g, w in user_genres.items()}
        
        # Trouver des films similaires (même genres)
        all_movies = self.db.get_all_movies()
        recommendations = []
        
        for movie in all_movies:
            if movie.id in [r.movie_id for r in ratings]:
                continue  # Exclure les films déjà notés
            
            if not movie.genres:
                continue
            
            # Calculer le score de similarité avec les préférences de l'utilisateur
            score = 0.0
            for genre in movie.genres:
                score += user_genres.get(genre, 0)
            
            if score > 0:
                recommendations.append(Recommendation(
                    movie=movie,
                    score=score,
                    reason=f"Correspond à vos genres préférés : {', '.join(movie.genres)}"
                ))
        
        # Trier par score décroissant
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    def get_collaborative_recommendations(
        self, user_id: int, limit: int = 5
    ) -> List[Recommendation]:
        """
        Génère des recommandations basées sur le filtrage collaboratif.
        Utilise une approche simple : "Les utilisateurs qui ont aimé les mêmes films que vous".
        """
        # Récupérer les notes de l'utilisateur
        user_ratings = self.db.get_ratings_by_user(user_id)
        if not user_ratings:
            return self.get_popular_recommendations(limit)
        
        # Trouver des utilisateurs similaires (qui ont noté les mêmes films)
        similar_users = []
        all_users = self.db.conn.execute("SELECT id FROM users").fetchall()
        
        for other_user_row in all_users:
            other_user_id = other_user_row["id"]
            if other_user_id == user_id:
                continue
            
            other_ratings = self.db.get_ratings_by_user(other_user_id)
            if not other_ratings:
                continue
            
            # Calculer la similarité (nombre de films en commun)
            common_movies = set(r.movie_id for r in user_ratings) & set(r.movie_id for r in other_ratings)
            if len(common_movies) >= 3:  # Seuil minimal pour considérer la similarité
                similarity = len(common_movies)
                similar_users.append((other_user_id, similarity))
        
        if not similar_users:
            return self.get_popular_recommendations(limit)
        
        # Trier les utilisateurs similaires par similarité
        similar_users.sort(key=lambda x: x[1], reverse=True)
        top_similar_user_id = similar_users[0][0]
        
        # Récupérer les films notés par l'utilisateur similaire mais pas par l'utilisateur actuel
        similar_user_ratings = self.db.get_ratings_by_user(top_similar_user_id)
        similar_user_movies = set(r.movie_id for r in similar_user_ratings)
        user_movies = set(r.movie_id for r in user_ratings)
        
        recommended_movie_ids = similar_user_movies - user_movies
        
        recommendations = []
        for movie_id in recommended_movie_ids:
            movie = self.db.get_movie_by_id(movie_id)
            if movie:
                # Récupérer la note donnée par l'utilisateur similaire
                rating = self.db.get_rating(top_similar_user_id, movie_id)
                if rating:
                    recommendations.append(Recommendation(
                        movie=movie,
                        score=rating.rating / 5.0,  # Normaliser entre 0 et 1
                        reason=f"Recommandé par un utilisateur similaire (note : {rating.rating}/5)"
                    ))
        
        # Trier par score décroissant
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    def get_hybrid_recommendations(
        self, user_id: int, limit: int = 5
    ) -> List[Recommendation]:
        """
        Génère des recommandations hybrides (collaboratif + contenu).
        """
        content_recs = self.get_content_based_recommendations(user_id, limit * 2)
        collaborative_recs = self.get_collaborative_recommendations(user_id, limit * 2)
        
        # Combiner les recommandations
        all_recs = content_recs + collaborative_recs
        
        # Supprimer les doublons (même film)
        unique_recs = []
        seen_movie_ids = set()
        for rec in all_recs:
            if rec.movie.id not in seen_movie_ids:
                seen_movie_ids.add(rec.movie.id)
                unique_recs.append(rec)
        
        # Trier par score moyen (si un film apparaît dans les deux listes, son score est la moyenne)
        combined_recs = []
        for movie_id in seen_movie_ids:
            movie_recs = [r for r in all_recs if r.movie.id == movie_id]
            avg_score = sum(r.score for r in movie_recs) / len(movie_recs)
            reason = "; ".join(r.reason for r in movie_recs)
            movie = movie_recs[0].movie
            combined_recs.append(Recommendation(
                movie=movie,
                score=avg_score,
                reason=reason
            ))
        
        combined_recs.sort(key=lambda x: x.score, reverse=True)
        return combined_recs[:limit]
    
    def get_popular_recommendations(self, limit: int = 5) -> List[Recommendation]:
        """
        Génère des recommandations basées sur les films les mieux notés globalement.
        """
        # Récupérer toutes les notes
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT movie_id, AVG(rating) as avg_rating, COUNT(*) as num_ratings
            FROM ratings
            GROUP BY movie_id
            HAVING num_ratings >= 5
            ORDER BY avg_rating DESC
            LIMIT ?
        """, (limit * 2,))
        
        recommendations = []
        for row in cursor.fetchall():
            movie = self.db.get_movie_by_id(row["movie_id"])
            if movie:
                recommendations.append(Recommendation(
                    movie=movie,
                    score=row["avg_rating"] / 5.0,  # Normaliser entre 0 et 1
                    reason=f"Film populaire (note moyenne : {row['avg_rating']:.1f}/5, {row['num_ratings']} notes)"
                ))
        
        return recommendations[:limit]
    
    def get_recommendations(
        self, user_id: int, method: str = "hybrid", limit: int = 5
    ) -> List[Recommendation]:
        """
        Génère des recommandations en utilisant la méthode spécifiée.
        
        Args:
            user_id: ID de l'utilisateur.
            method: Méthode de recommandation ("content", "collaborative", "hybrid", "popular").
            limit: Nombre maximal de recommandations.
        
        Returns:
            Liste de recommandations.
        """
        if method == "content":
            return self.get_content_based_recommendations(user_id, limit)
        elif method == "collaborative":
            return self.get_collaborative_recommendations(user_id, limit)
        elif method == "hybrid":
            return self.get_hybrid_recommendations(user_id, limit)
        elif method == "popular":
            return self.get_popular_recommendations(limit)
        else:
            raise ValueError(f"Méthode inconnue : {method}")
