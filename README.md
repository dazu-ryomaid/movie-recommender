# Movie Recommender System

Un système de recommandation de films/séries en Python avec gestion de comptes utilisateurs.

## 📌 Fonctionnalités
- **Dataset** : MovieLens 100k (1682 films + 100k notes utilisateurs).
- **Authentification** : Système de comptes utilisateurs (CLI et Web).
- **Recommandations** : Algorithmes collaboratifs, basés sur le contenu, et hybrides.
- **Interfaces** : CLI et **Web (Flask + Bootstrap)** pour interagir.

## 🚀 Installation

### 1. Cloner le repo
```bash
git clone https://github.com/dazu-ryomaid/movie-recommender.git
cd movie-recommender
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Télécharger le dataset MovieLens 100k
```bash
python scripts/download_dataset.py
```

### 4. Initialiser la base de données
```bash
python scripts/init_db.py
```

## 🌐 Lancer l'interface Web
```bash
cd web
python app.py
```
L'application sera disponible à l'adresse : [http://localhost:5000](http://localhost:5000)

## 📂 Structure du projet
```
movie-recommender/
├── data/                          # Dataset et base de données
│   ├── movie_recommender.db      # Base SQLite
│   └── .session                   # Session utilisateur (CLI)
├── web/                           # Interface Web (Flask)
│   ├── app.py                     # Application Flask
│   ├── templates/                # Templates HTML (Jinja2)
│   │   ├── base.html              # Template de base
│   │   ├── index.html             # Page d'accueil
│   │   ├── login.html             # Connexion
│   │   ├── signup.html            # Inscription
│   │   ├── rate.html              # Noter un film
│   │   ├── search.html            # Rechercher des films
│   │   ├── recommend.html          # Recommandations
│   │   ├── profile.html            # Profil utilisateur
│   │   └── movie_detail.html       # Détails d'un film
│   ├── static/                    # Fichiers statiques
│   │   └── style.css              # CSS personnalisé
│   └── .env                       # Configuration Flask
├── src/
│   ├── cli.py                     # Interface CLI
│   ├── database.py                # Gestion SQLite
│   ├── auth.py                    # Authentification
│   ├── recommender.py             # Algorithmes de recommandation
│   └── models.py                  # Modèles de données
├── scripts/
│   ├── download_dataset.py       # Téléchargement MovieLens
│   └── init_db.py                 # Initialisation de la BDD
├── main.py                        # Point d'entrée CLI
├── requirements.txt               # Dépendances
└── README.md
```

## 🔧 Utilisation

### Interface Web
1. Lancez le serveur Flask :
   ```bash
   cd web
   python app.py
   ```
2. Ouvrez [http://localhost:5000](http://localhost:5000) dans votre navigateur.
3. **Créez un compte** ou connectez-vous.
4. **Recherchez des films**, notez-les, et recevez des recommandations personnalisées !

### Interface CLI
Voir la section ci-dessous.

#### Commandes CLI
| Commande | Description | Exemple |
|----------|-------------|---------|
| `signup` | S'inscrire | `python main.py signup --username test --password 123` |
| `login` | Se connecter | `python main.py login --username test --password 123` |
| `rate` | Noter un film | `python main.py rate --movie "Toy Story" --rating 5` |
| `search` | Rechercher un film | `python main.py search --query "Matrix"` |
| `recommend` | Recommandations | `python main.py recommend --method hybrid --limit 5` |
| `profile` | Voir son profil | `python main.py my-ratings` |
| `genres` | Lister les genres | `python main.py genres` |
| `whoami` | Utilisateur connecté | `python main.py whoami` |
| `logout` | Se déconnecter | `python main.py logout` |

### Méthodes de recommandation
| Méthode | Description |
|---------|-------------|
| `hybrid` | Combinaison des méthodes collaboratives et basées sur le contenu (recommandé) |
| `content` | Basé sur les genres des films que vous avez notés |
| `collaborative` | Basé sur les notes des utilisateurs similaires |
| `popular` | Films les mieux notés globalement |

## 📊 Dataset
- **Source** : [MovieLens 100k](https://grouplens.org/datasets/movielens/100k/)
- **Contenu** : 1682 films, 100k notes utilisateurs, 19 genres.
- **Fichiers** :
  - `data/movies.raw` : Liste des films (ID, titre, genres, année).
  - `data/ratings.raw` : Notes des utilisateurs (userID, movieID, rating).

## 🛠️ Technos
- **Backend** : Python 3.10+, Flask, Flask-Login, Flask-WTF
- **Base de données** : SQLite
- **Data Science** : Pandas, Scikit-learn, Surprise
- **Frontend** : HTML5, Bootstrap 5, Jinja2
- **Authentification** : Hash SHA-256 (via Werkzeug)

## 🚀 Déploiement

### Déploiement local
1. Suivez les étapes d'installation ci-dessus.
2. Lancez l'application :
   ```bash
   cd web
   python app.py
   ```
3. Accédez à [http://localhost:5000](http://localhost:5000).

### Déploiement sur PythonAnywhere (gratuit)
1. **Créez un compte** sur [PythonAnywhere](https://www.pythonanywhere.com/) (gratuit pour les étudiants).
2. **Clonez le repo** :
   ```bash
   git clone https://github.com/dazu-ryomaid/movie-recommender.git
   ```
3. **Installez les dépendances** :
   ```bash
   pip install -r movie-recommender/requirements.txt
   ```
4. **Téléchargez le dataset** :
   ```bash
   cd movie-recommender
   python scripts/download_dataset.py
   python scripts/init_db.py
   ```
5. **Configurez l'application** :
   - Allez dans l'onglet **Web** de PythonAnywhere.
   - Sélectionnez **Manual configuration** (pas de framework).
   - Dans **Code**, ajoutez :
     ```python
     import sys
     sys.path.insert(0, '/home/votre_username/movie-recommender/web')
     from app import app as application
     ```
   - Dans **Working directory**, mettez : `/home/votre_username/movie-recommender/web`
6. **Lancez l'application** :
   - Cliquez sur **Reload** pour appliquer les changements.
   - Votre app sera disponible à : `https://votre_username.pythonanywhere.com`

### Déploiement sur Render (alternative)
1. **Créez un compte** sur [Render](https://render.com/) (gratuit pour les petits projets).
2. **Créez un nouveau Web Service** :
   - Liez votre repo GitHub.
   - **Build Command** : `pip install -r requirements.txt && cd web && python scripts/download_dataset.py && python scripts/init_db.py`
   - **Start Command** : `cd web && gunicorn -b 0.0.0.0:10000 app:app`
3. **Déployez** : Render va construire et déployer votre app.

## 🤝 Contribuer
Les contributions sont les bienvenues ! Ouvrez une **Pull Request** ou un **Issue** sur GitHub.

## 📜 Licence
MIT
