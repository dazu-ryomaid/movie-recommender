#!/usr/bin/env python3
"""
Interface en ligne de commande (CLI) pour le système de recommandation.
Gère les sessions utilisateurs via un fichier temporaire.
"""

import argparse
import os
import json
from pathlib import Path
from src.database import Database
from src.auth import AuthSystem
from src.recommender import RecommenderSystem
from src.models import Movie, Recommendation

# Chemin du fichier de session
SESSION_FILE = os.path.join("data", ".session")


class MovieRecommenderCLI:
    """CLI pour interagir avec le système de recommandation."""
    
    def __init__(self):
        self.db = Database()
        self.auth = AuthSystem(self.db)
        self.recommender = RecommenderSystem(self.db)
        self.current_user = self._load_session()
    
    def _load_session(self):
        """Charge la session utilisateur depuis le fichier de session."""
        if not os.path.exists(SESSION_FILE):
            return None
        try:
            with open(SESSION_FILE, "r") as f:
                session = json.load(f)
                user = self.db.get_user_by_id(session["user_id"])
                if user:
                    print(f"🔄 Session chargée : connecté en tant que {user.username}")
                    return user
        except (json.JSONDecodeError, KeyError):
            pass
        return None
    
    def _save_session(self, user):
        """Sauvegarde la session utilisateur dans un fichier."""
        Path("data").mkdir(parents=True, exist_ok=True)
        with open(SESSION_FILE, "w") as f:
            json.dump({"user_id": user.id}, f)
    
    def _clear_session(self):
        """Efface la session utilisateur."""
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    
    def signup(self, username: str, password: str):
        """Inscrire un nouvel utilisateur."""
        user = self.auth.signup(username, password)
        if user:
            self.current_user = user
            self._save_session(user)
            print(f"✅ Inscription réussie ! ID utilisateur : {user.id}")
    
    def login(self, username: str, password: str):
        """Connecter un utilisateur."""
        user = self.auth.login(username, password)
        if user:
            self.current_user = user
            self._save_session(user)
    
    def logout(self):
        """Déconnecter l'utilisateur actuel."""
        if self.current_user:
            print(f"👋 Déconnexion de {self.current_user.username}")
            self._clear_session()
            self.current_user = None
        else:
            print("❌ Aucun utilisateur connecté.")
    
    def rate_movie(self, movie_title: str, rating: int):
        """Noter un film."""
        if not self.current_user:
            print("❌ Vous devez être connecté pour noter un film. Utilisez 'login' ou 'signup'.")
            return
        
        movie = self.db.search_movies(movie_title, limit=1)
        if not movie:
            print(f"❌ Film '{movie_title}' introuvable.")
            return
        
        movie = movie[0]
        print(f"🎬 Film trouvé : {movie.title} ({movie.year})")
        
        if rating < 1 or rating > 5:
            print("❌ La note doit être entre 1 et 5.")
            return
        
        # Ajouter la note
        self.db.add_rating(self.current_user.id, movie.id, rating)
        print(f"✅ Note ajoutée : {rating}/5 pour '{movie.title}'")
    
    def search_movies(self, query: str, limit: int = 10):
        """Rechercher des films."""
        movies = self.db.search_movies(query, limit)
        if not movies:
            print(f"❌ Aucun film trouvé pour '{query}'.")
            return
        
        print(f"\n🔍 Résultats pour '{query}' :")
        for i, movie in enumerate(movies, 1):
            genres = ", ".join(movie.genres) if movie.genres else "Inconnu"
            print(f"{i}. {movie.title} ({movie.year}) - Genres : {genres}")
    
    def get_recommendations(self, method: str = "hybrid", limit: int = 5):
        """Obtenir des recommandations."""
        if not self.current_user:
            print("❌ Vous devez être connecté pour obtenir des recommandations.")
            return
        
        print(f"\n🎯 Génération de recommandations (méthode : {method})...")
        recommendations = self.recommender.get_recommendations(
            self.current_user.id, method=method, limit=limit
        )
        
        if not recommendations:
            print("❌ Aucune recommandation trouvée.")
            return
        
        print(f"\n🌟 Recommandations pour {self.current_user.username} :")
        for i, rec in enumerate(recommendations, 1):
            genres = ", ".join(rec.movie.genres) if rec.movie.genres else "Inconnu"
            print(f"\n{i}. {rec.movie.title} ({rec.movie.year})")
            print(f"   📌 Genres : {genres}")
            print(f"   ⭐ Score : {rec.score:.2f}")
            print(f"   💡 Pourquoi ? {rec.reason}")
    
    def list_genres(self):
        """Lister tous les genres disponibles."""
        genres = self.db.get_all_genres()
        print("\n🎭 Genres disponibles :")
        for i, genre in enumerate(genres, 1):
            print(f"{i}. {genre}")
    
    def my_ratings(self):
        """Afficher les notes de l'utilisateur actuel."""
        if not self.current_user:
            print("❌ Vous devez être connecté pour voir vos notes.")
            return
        
        ratings = self.db.get_ratings_by_user(self.current_user.id)
        if not ratings:
            print("❌ Vous n'avez pas encore noté de films.")
            return
        
        print(f"\n📝 Notes de {self.current_user.username} :")
        for i, rating in enumerate(ratings, 1):
            movie = self.db.get_movie_by_id(rating.movie_id)
            if movie:
                print(f"{i}. {movie.title} : {rating.rating}/5")
    
    def whoami(self):
        """Affiche l'utilisateur actuellement connecté."""
        if self.current_user:
            print(f"👤 Connecté en tant que : {self.current_user.username} (ID: {self.current_user.id})")
        else:
            print("❌ Aucun utilisateur connecté.")
    
    def run(self):
        """Lance l'interface CLI."""
        parser = argparse.ArgumentParser(
            description="Système de recommandation de films - CLI"
        )
        subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
        
        # Commande signup
        signup_parser = subparsers.add_parser("signup", help="S'inscrire")
        signup_parser.add_argument("--username", required=True, help="Nom d'utilisateur")
        signup_parser.add_argument("--password", required=True, help="Mot de passe")
        
        # Commande login
        login_parser = subparsers.add_parser("login", help="Se connecter")
        login_parser.add_argument("--username", required=True, help="Nom d'utilisateur")
        login_parser.add_argument("--password", required=True, help="Mot de passe")
        
        # Commande logout
        subparsers.add_parser("logout", help="Se déconnecter")
        
        # Commande rate
        rate_parser = subparsers.add_parser("rate", help="Noter un film")
        rate_parser.add_argument("--movie", required=True, help="Titre du film")
        rate_parser.add_argument("--rating", type=int, required=True, help="Note (1-5)")
        
        # Commande search
        search_parser = subparsers.add_parser("search", help="Rechercher des films")
        search_parser.add_argument("--query", required=True, help="Recherche")
        search_parser.add_argument("--limit", type=int, default=10, help="Nombre de résultats")
        
        # Commande recommend
        recommend_parser = subparsers.add_parser("recommend", help="Obtenir des recommandations")
        recommend_parser.add_argument(
            "--method", 
            choices=["content", "collaborative", "hybrid", "popular"],
            default="hybrid",
            help="Méthode de recommandation (défaut: hybrid)"
        )
        recommend_parser.add_argument("--limit", type=int, default=5, help="Nombre de recommandations")
        
        # Commande genres
        subparsers.add_parser("genres", help="Lister les genres")
        
        # Commande my-ratings
        subparsers.add_parser("my-ratings", help="Voir mes notes")
        
        # Commande whoami
        subparsers.add_parser("whoami", help="Voir l'utilisateur connecté")
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # Exécuter la commande
        if args.command == "signup":
            self.signup(args.username, args.password)
        elif args.command == "login":
            self.login(args.username, args.password)
        elif args.command == "logout":
            self.logout()
        elif args.command == "rate":
            self.rate_movie(args.movie, args.rating)
        elif args.command == "search":
            self.search_movies(args.query, args.limit)
        elif args.command == "recommend":
            self.get_recommendations(args.method, args.limit)
        elif args.command == "genres":
            self.list_genres()
        elif args.command == "my-ratings":
            self.my_ratings()
        elif args.command == "whoami":
            self.whoami()
        else:
            parser.print_help()


if __name__ == "__main__":
    cli = MovieRecommenderCLI()
    cli.run()
