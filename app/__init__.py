# app/__init__.py

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, template_folder='templates')  # ensure templates folder is set

    # --- Configurations ---
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/bookstore_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'
    app.config.from_object("app.config.Config")  # optional if you have extra config

    # --- Initialize extensions with app ---
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # --- Import models ---
    from app import models

    # --- Home route using template ---
    @app.route('/')
    def home():
        return render_template('home.html')  # render the home.html template

    # --- Register blueprints ---
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # --- Create database tables ---
    with app.app_context():
        db.create_all()

    return app
