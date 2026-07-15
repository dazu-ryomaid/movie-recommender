#!/usr/bin/env python3
"""
Point d'entrée principal pour le système de recommandation.
"""

from src.cli import MovieRecommenderCLI

if __name__ == "__main__":
    cli = MovieRecommenderCLI()
    cli.run()
