#!/usr/bin/env python3
"""
Système d'authentification pour le projet de recommandation.
"""

import hashlib
from typing import Optional
from src.database import Database
from src.models import User


class AuthSystem:
    """Classe pour gérer l'authentification des utilisateurs."""
    
    def __init__(self, db: Database):
        self.db = db
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash un mot de passe en SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def signup(self, username: str, password: str) -> Optional[User]:
        """
        Inscrire un nouvel utilisateur.
        Retourne l'utilisateur créé ou None si le nom d'utilisateur existe déjà.
        """
        # Vérifier si l'utilisateur existe déjà
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            print(f"❌ L'utilisateur '{username}' existe déjà.")
            return None
        
        # Hasher le mot de passe
        hashed_password = self.hash_password(password)
        
        # Créer l'utilisateur
        user = self.db.create_user(username, hashed_password)
        print(f"✅ Utilisateur '{username}' créé avec succès !")
        return user
    
    def login(self, username: str, password: str) -> Optional[User]:
        """
        Connecter un utilisateur.
        Retourne l'utilisateur si les identifiants sont corrects, None sinon.
        """
        user = self.db.get_user_by_username(username)
        if not user:
            print(f"❌ Utilisateur '{username}' introuvable.")
            return None
        
        # Vérifier le mot de passe
        hashed_password = self.hash_password(password)
        if user.password != hashed_password:
            print("❌ Mot de passe incorrect.")
            return None
        
        print(f"✅ Connexion réussie pour '{username}' !")
        return user
    
    def get_current_user(self, user_id: int) -> Optional[User]:
        """Récupère l'utilisateur actuel par son ID."""
        return self.db.get_user_by_id(user_id)
