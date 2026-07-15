#!/usr/bin/env python3
"""
Script pour télécharger le dataset MovieLens 100k.
Source : https://files.grouplens.org/datasets/movielens/ml-100k.zip
"""

import os
import zipfile
import requests
from pathlib import Path

# URLs du dataset
DATASET_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
DATASET_ZIP = "data/ml-100k.zip"
DATASET_DIR = "data"

# Fichiers à extraire
FILES_TO_EXTRACT = ["ml-100k/u.data", "ml-100k/u.item", "ml-100k/u.user"]


def download_dataset():
    """Télécharge le dataset MovieLens 100k."""
    print("⏳ Téléchargement du dataset MovieLens 100k...")
    
    # Créer le dossier data s'il n'existe pas
    Path(DATASET_DIR).mkdir(parents=True, exist_ok=True)
    
    # Télécharger le fichier ZIP
    response = requests.get(DATASET_URL, stream=True)
    if response.status_code != 200:
        print(f"❌ Échec du téléchargement : {response.status_code}")
        return False
    
    # Sauvegarder le ZIP
    with open(DATASET_ZIP, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("✅ Dataset téléchargé avec succès !")
    
    # Extraire les fichiers nécessaires
    print("⏳ Extraction des fichiers...")
    with zipfile.ZipFile(DATASET_ZIP, "r") as zip_ref:
        for file in FILES_TO_EXTRACT:
            zip_ref.extract(file, DATASET_DIR)
    
    # Renommer les fichiers pour plus de clarté
    os.rename(
        os.path.join(DATASET_DIR, "ml-100k/u.data"),
        os.path.join(DATASET_DIR, "ratings.raw")
    )
    os.rename(
        os.path.join(DATASET_DIR, "ml-100k/u.item"),
        os.path.join(DATASET_DIR, "movies.raw")
    )
    os.rename(
        os.path.join(DATASET_DIR, "ml-100k/u.user"),
        os.path.join(DATASET_DIR, "users.raw")
    )
    
    # Supprimer le ZIP après extraction
    os.remove(DATASET_ZIP)
    print("✅ Fichiers extraits et nettoyés !")
    
    return True


if __name__ == "__main__":
    download_dataset()
