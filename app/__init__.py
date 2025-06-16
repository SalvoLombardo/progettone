# app/__init__.py
from flask import Flask,jsonify
from .extensions import db, bcrypt, login_manager, migrate , jwt ,csrf
from flask_jwt_extended import JWTManager
from datetime import timedelta

from .main import main_bp
from .auth import auth_bp
from .admin import admin_bp
from .api import api_bp

from .models import User,User_JWT,TokenBlocklist


import os

def create_app():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)  
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    
    from dotenv import load_dotenv
    load_dotenv()  # Carica da .env
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    

    

    uri = os.getenv("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
   

    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    from . import jwt_callbacks 


    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    #####Con queste righe applichiamo con una sola riga di html il CSRF token a tutti i form######
    #####Senza necessità di usare un FlaskForm#####
    from flask_wtf.csrf import generate_csrf
    app.jinja_env.globals['csrf_token'] = generate_csrf
    #####il codice html è questo : <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">######


    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    csrf.exempt(api_bp)  # Qui escludi tutto il blueprint API dal CSRF poichè non si usa nelle parti con API


    


    
    return app


__all__ = ["create_app"]