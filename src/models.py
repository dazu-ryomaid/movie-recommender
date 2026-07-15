#!/usr/bin/env python3
"""
Modèles de données pour le système de recommandation.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Movie:
    """Représente un film."""
    id: int
    title: str
    year: Optional[int] = None
    genres: Optional[List[str]] = None


@dataclass
class User:
    """Représente un utilisateur."""
    id: int
    username: str
    password: str  # En pratique, ce serait un hash


@dataclass
class Rating:
    """Représente une note donnée par un utilisateur à un film."""
    user_id: int
    movie_id: int
    rating: int  # Note de 1 à 5


@dataclass
class Recommendation:
    """Représente une recommandation de film."""
    movie: Movie
    score: float  # Score de recommandation (0.0 à 1.0)
    reason: str  # Raison de la recommandation (ex: "Similaire à Inception")
