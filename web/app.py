#!/usr/bin/env python3
"""
Application Flask pour le système de recommandation de films.
"""

import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.database import Database
from src.recommender import RecommenderSystem

# Initialisation Flask
app = Flask(__name__)

# Configuration manuelle (au lieu de from_pyfile pour éviter les problèmes)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['FLASK_ENV'] = 'development'
app.config['SESSION_TYPE'] = 'filesystem'

# Configuration Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Initialisation de la base de données et du système de recommandation
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "movie_recommender.db")
db = Database(DB_PATH)
recommender = RecommenderSystem(db)


# Modèle utilisateur pour Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.id
        self.username = user_data.username
        self.password_hash = user_data.password


@login_manager.user_loader
def load_user(user_id):
    """Charge un utilisateur depuis la base de données."""
    user_data = db.get_user_by_id(int(user_id))
    if user_data:
        return User(user_data)
    return None


# Formulaires WTForms
class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")


class SignupForm(FlaskForm):
    username = StringField(
        "Nom d'utilisateur", 
        validators=[DataRequired(), Length(min=4, max=20)]
    )
    password = PasswordField(
        "Mot de passe", 
        validators=[DataRequired(), Length(min=6)]
    )
    submit = SubmitField("S'inscrire")


class RateForm(FlaskForm):
    movie_title = StringField("Titre du film", validators=[DataRequired()])
    rating = IntegerField(
        "Note (1-5)", 
        validators=[DataRequired(), NumberRange(min=1, max=5)]
    )
    submit = SubmitField("Noter")


class SearchForm(FlaskForm):
    query = StringField("Rechercher un film", validators=[DataRequired()])
    submit = SubmitField("Rechercher")


# Routes
@app.route("/")
def index():
    """Page d'accueil."""
    if current_user.is_authenticated:
        # Afficher les recommandations pour l'utilisateur connecté
        recommendations = recommender.get_recommendations(
            current_user.id, method="hybrid", limit=5
        )
        return render_template(
            "index.html", 
            recommendations=recommendations,
            current_user=current_user
        )
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user_data = db.get_user_by_username(form.username.data)
        if user_data and check_password_hash(user_data.password, form.password.data):
            user = User(user_data)
            login_user(user)
            flash("Connexion réussie !", "success")
            return redirect(url_for("index"))
        flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")
    return render_template("login.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Page d'inscription."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = SignupForm()
    if form.validate_on_submit():
        # Vérifier si l'utilisateur existe déjà
        if db.get_user_by_username(form.username.data):
            flash("Ce nom d'utilisateur est déjà pris.", "danger")
            return redirect(url_for("signup"))
        
        # Hasher le mot de passe et créer l'utilisateur
        password_hash = generate_password_hash(form.password.data)
        user_data = db.create_user(form.username.data, password_hash)
        user = User(user_data)
        login_user(user)
        flash("Inscription réussie !", "success")
        return redirect(url_for("index"))
    return render_template("signup.html", form=form)


@app.route("/logout")
@login_required
def logout():
    """Déconnexion."""
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for("index"))


@app.route("/rate", methods=["GET", "POST"])
@login_required
def rate():
    """Noter un film."""
    form = RateForm()
    if form.validate_on_submit():
        movie = db.search_movies(form.movie_title.data, limit=1)
        if not movie:
            flash(f"Film '{form.movie_title.data}' introuvable.", "danger")
            return redirect(url_for("rate"))
        
        movie = movie[0]
        db.add_rating(current_user.id, movie.id, form.rating.data)
        flash(f"Note ajoutée : {form.rating.data}/5 pour '{movie.title}' !", "success")
        return redirect(url_for("profile"))
    
    return render_template("rate.html", form=form)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Rechercher des films."""
    form = SearchForm()
    movies = []
    if form.validate_on_submit():
        movies = db.search_movies(form.query.data, limit=10)
    return render_template("search.html", form=form, movies=movies)


@app.route("/recommend", methods=["GET"])
@login_required
def recommend():
    """Page de recommandations."""
    method = request.args.get("method", "hybrid")
    limit = int(request.args.get("limit", 10))
    
    recommendations = recommender.get_recommendations(
        current_user.id, method=method, limit=limit
    )
    
    return render_template(
        "recommend.html", 
        recommendations=recommendations,
        method=method,
        current_user=current_user
    )


@app.route("/profile")
@login_required
def profile():
    """Page de profil utilisateur."""
    ratings = db.get_ratings_by_user(current_user.id)
    rated_movies = []
    for rating in ratings:
        movie = db.get_movie_by_id(rating.movie_id)
        if movie:
            rated_movies.append((movie, rating.rating))
    
    return render_template(
        "profile.html", 
        user=current_user,
        rated_movies=rated_movies
    )


@app.route("/movie/<int:movie_id>")
@login_required
def movie_detail(movie_id):
    """Détails d'un film."""
    movie = db.get_movie_by_id(movie_id)
    if not movie:
        flash("Film introuvable.", "danger")
        return redirect(url_for("index"))
    
    # Vérifier si l'utilisateur a déjà noté ce film
    user_rating = db.get_rating(current_user.id, movie_id)
    
    return render_template(
        "movie_detail.html", 
        movie=movie,
        user_rating=user_rating
    )


# Erreur 404 personnalisée
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
