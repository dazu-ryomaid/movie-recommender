#!/usr/bin/env python3
"""
Script pour initialiser la base de données SQLite à partir du dataset MovieLens.
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

# Chemins des fichiers
DATA_DIR = "data"
MOVIES_RAW = os.path.join(DATA_DIR, "movies.raw")
RATINGS_RAW = os.path.join(DATA_DIR, "ratings.raw")
USERS_RAW = os.path.join(DATA_DIR, "users.raw")
DB_PATH = os.path.join(DATA_DIR, "movie_recommender.db")


def parse_movies(file_path: str) -> pd.DataFrame:
    """
    Parse le fichier u.item (movies) du dataset MovieLens.
    Format : movie_id|title|release_date|video_release_date|IMDb_URL|unknown|Action|Adventure|...|genre
    """
    columns = [
        "movie_id", "title", "release_date", "video_release_date", "imdb_url",
        "unknown", "Action", "Adventure", "Animation", "Children", "Comedy",
        "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror",
        "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"
    ]
    df = pd.read_csv(file_path, sep="|", header=None, names=columns, encoding="latin-1")
    
    # Extraire les genres (colonnes 5 à 24)
    genres = df.columns[5:]
    df["genres"] = df[genres].apply(
        lambda row: "|".join([genre for genre, val in zip(genres, row) if val == 1]),
        axis=1
    )
    
    # Nettoyer le titre (enlever l'année entre parenthèses)
    df["title"] = df["title"].str.replace(r" \(\d{4}\)", "", regex=True)
    
    # Garder seulement les colonnes utiles
    df = df[["movie_id", "title", "release_date", "genres"]]
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
    df.rename(columns={"release_date": "year"}, inplace=True)
    
    return df


def parse_ratings(file_path: str) -> pd.DataFrame:
    """
    Parse le fichier u.data (ratings) du dataset MovieLens.
    Format : user_id|movie_id|rating|timestamp
    """
    columns = ["user_id", "movie_id", "rating", "timestamp"]
    df = pd.read_csv(file_path, sep="\t", header=None, names=columns)
    return df


def parse_users(file_path: str) -> pd.DataFrame:
    """
    Parse le fichier u.user (users) du dataset MovieLens.
    Format : user_id|age|gender|occupation|zip_code
    """
    columns = ["user_id", "age", "gender", "occupation", "zip_code"]
    df = pd.read_csv(file_path, sep="|", header=None, names=columns)
    return df


def init_db():
    """Initialise la base de données SQLite."""
    print("⏳ Initialisation de la base de données...")
    
    # Vérifier que les fichiers raw existent
    if not all(os.path.exists(f) for f in [MOVIES_RAW, RATINGS_RAW, USERS_RAW]):
        print("❌ Fichiers raw introuvables. Exécutez d'abord : python scripts/download_dataset.py")
        return False
    
    # Connexion à la base de données
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Créer les tables
    print("⏳ Création des tables...")
    
    # Table movies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER,
            genres TEXT
        )
    """)
    
    # Table users (pour les utilisateurs du système, pas ceux de MovieLens)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # Table ratings (notes des utilisateurs du système)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
    """)
    
    # Table user_preferences (préférences explicites, ex: genres favoris)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER NOT NULL,
            genre TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            PRIMARY KEY (user_id, genre),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Charger les films depuis le dataset MovieLens
    print("⏳ Chargement des films...")
    movies_df = parse_movies(MOVIES_RAW)
    
    # Insérer les films dans la base de données
    for _, row in movies_df.iterrows():
        cursor.execute(
            "INSERT OR IGNORE INTO movies (id, title, year, genres) VALUES (?, ?, ?, ?)",
            (row["movie_id"], row["title"], row["year"], row["genres"])
        )
    
    conn.commit()
    print(f"✅ {len(movies_df)} films chargés dans la base de données !")
    
    # Charger les notes depuis le dataset MovieLens (optionnel, pour avoir des données de base)
    print("⏳ Chargement des notes MovieLens (pour démonstration)...")
    ratings_df = parse_ratings(RATINGS_RAW)
    
    # Créer un utilisateur fictif pour les données MovieLens (ID 0)
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, username, password) VALUES (0, 'movielens_user', 'demo')"
    )
    
    # Insérer les notes dans la base de données (en les associant à l'utilisateur fictif)
    for _, row in ratings_df.iterrows():
        cursor.execute(
            "INSERT OR IGNORE INTO ratings (user_id, movie_id, rating) VALUES (?, ?, ?)",
            (0, row["movie_id"], row["rating"])
        )
    
    conn.commit()
    print(f"✅ {len(ratings_df)} notes chargées dans la base de données !")
    
    conn.close()
    print("✅ Base de données initialisée avec succès !")
    return True


if __name__ == "__main__":
    init_db()
