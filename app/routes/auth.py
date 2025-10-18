from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Book
from flask_jwt_extended import create_access_token
from flask_jwt_extended import JWTManager

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# -------------------------------
# Register
# -------------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or email already exists'}), 409

    hashed_pw = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    # CREATE TOKEN USING ONLY USER ID AS STRING
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'token': access_token, 'username': user.username}), 200


# -------------------------------
# Login
# -------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # CREATE TOKEN USING ONLY USER ID AS STRING
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'token': access_token, 'username': user.username}), 200


# -------------------------------
# Home
# -------------------------------
@auth_bp.route('/')
def home():
    books = Book.query.all()
    return render_template('home.html', books=books)


# -------------------------------
# Login/Register Pages
# -------------------------------
@auth_bp.route('/login-page')
def login_page():
    return render_template('login.html')


@auth_bp.route('/register-page')
def register_page():
    return render_template('register.html')
