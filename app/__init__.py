from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from datetime import timedelta


db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    template_path = os.path.join(os.getcwd(), "templates")
    static_path = os.path.join(os.getcwd(), "app", "static")
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)

    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7) 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/bookstore_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    # Import blueprints
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.cart import cart_bp
    from app.routes.debug import debug_bp
    
    # Register blueprints
    app.register_blueprint(debug_bp)
    app.register_blueprint(auth_bp)  # No prefix - routes at root level
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        from app.utils.image_assigner import assign_images
        assign_images()

    return app
