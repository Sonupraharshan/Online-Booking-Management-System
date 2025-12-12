from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Book
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)


# -------------------------------
# Home Page with Category Filtering and Search
# -------------------------------
@auth_bp.route('/')
def home():
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'newest')
    search = request.args.get('search', '')
    
    query = Book.query
    
    # Search by title or author
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term)
            )
        )
    
    # Filter by category/genre if specified (check both category and genres fields)
    if category:
        query = query.filter(
            db.or_(
                Book.category == category,
                Book.genres.ilike(f'%{category}%')
            )
        )
    
    # Sort options
    if sort == 'price_asc':
        query = query.order_by(Book.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Book.price.desc())
    elif sort == 'title':
        query = query.order_by(Book.title.asc())
    else:  # newest
        query = query.order_by(Book.created_at.desc())
    
    books = query.all()
    
    # Build genre counts from all books' genres
    genre_counts = {}
    all_books = Book.query.all()
    for book in all_books:
        for genre in book.genres_list:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    # Sort genres by count
    categories = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    
    return render_template('home.html', 
                          books=books, 
                          categories=categories,
                          current_category=category,
                          current_sort=sort,
                          current_search=search)


# -------------------------------
# Book Detail Page
# -------------------------------
@auth_bp.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    # Get related books (same category)
    related = Book.query.filter(Book.category == book.category, Book.id != book.id).limit(4).all()
    return render_template('book_detail.html', book=book, related=related)


# -------------------------------
# Login Page & API
# -------------------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST - API login
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'token': access_token, 
        'username': user.username,
        'role': user.role  # Include role in response
    }), 200


# -------------------------------
# Register Page & API
# -------------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    # POST - API register
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

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'token': access_token, 
        'username': user.username,
        'role': user.role
    }), 200
