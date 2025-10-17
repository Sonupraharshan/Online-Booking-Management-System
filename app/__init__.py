# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # --- Configurations ---
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/bookstore_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'
    app.config.from_object("app.config.Config")

    # --- Initialize extensions with app ---
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # --- Import and register blueprints ---
    # from .routes import main_routes
    # app.register_blueprint(main_routes)
    from . import models
    # --- Simple test route ---
    @app.route('/')
    def home():
        return "Hello! Your Online Booking System Flask app is running."

    # --- Create database tables if they don't exist ---
    with app.app_context():
        db.create_all()
        from app.routes.auth import auth_bp
        app.register_blueprint(auth_bp)


    return app
