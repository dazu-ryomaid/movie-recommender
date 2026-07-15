# Movie Recommender System

Un système de recommandation de films/séries en Python avec gestion de comptes utilisateurs.

## 📌 Fonctionnalités
- **Dataset** : MovieLens 100k (films + notes utilisateurs).
- **Authentification** : Système de comptes utilisateurs (CLI).
- **Recommandations** : Algorithmes collaboratifs et basés sur le contenu.
- **Interface** : CLI pour interagir (login, noter des films, recevoir des recommandations).

## 🚀 Installation

1. Cloner le repo :
   ```bash
   git clone https://github.com/dazu-ryomaid/movie-recommender.git
   cd movie-recommender
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Télécharger le dataset MovieLens 100k :
   ```bash
   python scripts/download_dataset.py
   ```

4. Initialiser la base de données :
   ```bash
   python scripts/init_db.py
   ```

5. Lancer l'interface CLI :
   ```bash
   python src/cli.py
   ```

## 📂 Structure du projet
```
movie-recommender/
├── data/                  # Dataset (movies.csv, ratings.csv)
├── src/
│   ├── cli.py             # Interface CLI
│   ├── database.py        # Gestion SQLite
│   ├── auth.py            # Authentification
│   ├── recommender.py     # Algorithmes de recommandation
│   └── models.py          # Modèles de données
├── scripts/
│   ├── download_dataset.py # Téléchargement du dataset
│   └── init_db.py         # Initialisation de la BDD
├── requirements.txt       # Dépendances
└── README.md
```

## 🔧 Utilisation

### 1. Créer un compte
```bash
python src/cli.py --signup --username <ton_username> --password <ton_password>
```

### 2. Se connecter
```bash
python src/cli.py --login --username <ton_username> --password <ton_password>
```

### 3. Noter un film
```bash
python src/cli.py --rate --movie "Toy Story" --rating 5
```

### 4. Recevoir des recommandations
```bash
python src/cli.py --recommend
```

## 📊 Dataset
- **Source** : [MovieLens 100k](https://grouplens.org/datasets/movielens/100k/)
- **Fichiers** :
  - `data/movies.csv` : Liste des films (ID, titre, genres).
  - `data/ratings.csv` : Notes des utilisateurs (userID, movieID, rating).

## 🛠️ Technos
- **Python 3.10+**
- **SQLite** (base de données légère)
- **Pandas** (manipulation des données)
- **Scikit-learn** (algorithmes de recommandation)
- **Surprise** (librairie pour les systèmes de recommandation)
