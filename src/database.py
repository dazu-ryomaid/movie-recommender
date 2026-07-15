#!/usr/bin/env python3
"""
Gestion de la base de données SQLite.
"""

import sqlite3
import os
from typing import List, Optional, Tuple
from src.models import Movie, User, Rating

# Chemin de la base de données
DB_PATH = os.path.join("data", "movie_recommender.db")


class Database:
    """Classe pour gérer la base de données SQLite."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
    
    def __del__(self):
        if self.conn:
            self.conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par son nom d'utilisateur."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return User(id=row["id"], username=row["username"], password=row["password"])
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par son ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, username, password FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return User(id=row["id"], username=row["username"], password=row["password"])
        return None
    
    def create_user(self, username: str, password: str) -> User:
        """Crée un nouvel utilisateur."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        self.conn.commit()
        user_id = cursor.lastrowid
        return User(id=user_id, username=username, password=password)
    
    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        """Récupère un film par son ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, title, year, genres FROM movies WHERE id = ?",
            (movie_id,)
        )
        row = cursor.fetchone()
        if row:
            genres = row["genres"].split("|") if row["genres"] else []
            return Movie(
                id=row["id"],
                title=row["title"],
                year=row["year"],
                genres=genres
            )
        return None
    
    def get_movie_by_title(self, title: str) -> Optional[Movie]:
        """Récupère un film par son titre (recherche insensible à la casse)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, title, year, genres FROM movies WHERE LOWER(title) LIKE LOWER(?)",
            (f"%{title}%",)
        )
        row = cursor.fetchone()
        if row:
            genres = row["genres"].split("|") if row["genres"] else []
            return Movie(
                id=row["id"],
                title=row["title"],
                year=row["year"],
                genres=genres
            )
        return None
    
    def search_movies(self, query: str, limit: int = 10) -> List[Movie]:
        """Recherche des films par titre (recherche partielle)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, title, year, genres FROM movies WHERE LOWER(title) LIKE LOWER(?) LIMIT ?",
            (f"%{query}%", limit)
        )
        movies = []
        for row in cursor.fetchall():
            genres = row["genres"].split("|") if row["genres"] else []
            movies.append(Movie(
                id=row["id"],
                title=row["title"],
                year=row["year"],
                genres=genres
            ))
        return movies
    
    def get_all_movies(self, limit: int = None) -> List[Movie]:
        """Récupère tous les films (optionnellement limité)."""
        cursor = self.conn.cursor()
        query = "SELECT id, title, year, genres FROM movies"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        movies = []
        for row in cursor.fetchall():
            genres = row["genres"].split("|") if row["genres"] else []
            movies.append(Movie(
                id=row["id"],
                title=row["title"],
                year=row["year"],
                genres=genres
            ))
        return movies
    
    def get_ratings_by_user(self, user_id: int) -> List[Rating]:
        """Récupère toutes les notes d'un utilisateur."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_id, movie_id, rating FROM ratings WHERE user_id = ?",
            (user_id,)
        )
        ratings = []
        for row in cursor.fetchall():
            ratings.append(Rating(
                user_id=row["user_id"],
                movie_id=row["movie_id"],
                rating=row["rating"]
            ))
        return ratings
    
    def get_rating(self, user_id: int, movie_id: int) -> Optional[Rating]:
        """Récupère la note d'un utilisateur pour un film spécifique."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_id, movie_id, rating FROM ratings WHERE user_id = ? AND movie_id = ?",
            (user_id, movie_id)
        )
        row = cursor.fetchone()
        if row:
            return Rating(
                user_id=row["user_id"],
                movie_id=row["movie_id"],
                rating=row["rating"]
            )
        return None
    
    def add_rating(self, user_id: int, movie_id: int, rating: int) -> Rating:
        """Ajoute ou met à jour une note."""
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO ratings (user_id, movie_id, rating) 
               VALUES (?, ?, ?) 
               ON CONFLICT(user_id, movie_id) DO UPDATE SET rating = ?""",
            (user_id, movie_id, rating, rating)
        )
        self.conn.commit()
        return Rating(user_id=user_id, movie_id=movie_id, rating=rating)
    
    def get_movies_by_genre(self, genre: str, limit: int = 10) -> List[Movie]:
        """Récupère des films par genre."""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT id, title, year, genres FROM movies 
               WHERE genres LIKE ? 
               LIMIT ?""",
            (f"%{genre}%", limit)
        )
        movies = []
        for row in cursor.fetchall():
            genres = row["genres"].split("|") if row["genres"] else []
            movies.append(Movie(
                id=row["id"],
                title=row["title"],
                year=row["year"],
                genres=genres
            ))
        return movies
    
    def get_all_genres(self) -> List[str]:
        """Récupère tous les genres uniques."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT genres FROM movies")
        genres_set = set()
        for row in cursor.fetchall():
            if row["genres"]:
                genres_set.update(row["genres"].split("|"))
        return sorted(list(genres_set))
    
    def get_user_preferences(self, user_id: int) -> List[Tuple[str, float]]:
        """Récupère les préférences de genre d'un utilisateur."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT genre, weight FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchall()
    
    def add_user_preference(self, user_id: int, genre: str, weight: float = 1.0):
        """Ajoute ou met à jour une préférence de genre pour un utilisateur."""
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO user_preferences (user_id, genre, weight) 
               VALUES (?, ?, ?) 
               ON CONFLICT(user_id, genre) DO UPDATE SET weight = ?""",
            (user_id, genre, weight, weight)
        )
        self.conn.commit()
