from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask import abort
from app import db
from app.models import Book, User
from functools import wraps
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Configure where images will be saved
UPLOAD_FOLDER = 'app/static/images/books'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def admin_api_required(fn):
    """Decorator to require admin role for API routes (JSON requests)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
        except Exception as e:
            return jsonify({'error': 'Authentication required'}), 401
        return fn(*args, **kwargs)
    return wrapper


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def auto_assign_image(book):
    """
    Assign an image automatically if none is uploaded.
    """
    images_path = os.path.join(os.getcwd(), UPLOAD_FOLDER)
    images = os.listdir(images_path) if os.path.exists(images_path) else []

    for img in images:
        if book.title.lower().replace(" ", "_") in img.lower() or book.author.lower().split()[0] in img.lower():
            return img

    return images[0] if images else None


# -------------------------------
# Admin Dashboard (Public page, JS checks role)
# -------------------------------
@admin_bp.route('/')
def dashboard():
    """Admin dashboard - page is public, JS checks if user is admin"""
    book_count = Book.query.count()
    categories = db.session.query(Book.category, db.func.count(Book.id)).group_by(Book.category).all()
    return render_template('admin/dashboard.html', book_count=book_count, categories=categories)


# -------------------------------
# Import Books from Open Library
# -------------------------------
@admin_bp.route('/import-books', methods=['GET', 'POST'])
def import_books():
    """Search and import books from Open Library API"""
    if request.method == 'GET':
        return render_template('admin/import_books.html', books=[], query='')
    
    # POST - Search Open Library
    query = request.form.get('query', '')
    if not query:
        return render_template('admin/import_books.html', books=[], query='', error='Please enter a search term')
    
    from app.utils.book_fetcher import search_books
    books = search_books(query)
    return render_template('admin/import_books.html', books=books, query=query)


@admin_bp.route('/import-book', methods=['POST'])
def import_single_book():
    """Import a single book from Open Library data"""
    from app.utils.book_fetcher import download_cover, get_book_description, get_all_genres
    
    title = request.form.get('title')
    author = request.form.get('author')
    cover_id = request.form.get('cover_id')
    isbn = request.form.get('isbn', '')
    category = request.form.get('category', 'General')
    price = float(request.form.get('price', 9.99))
    work_key = request.form.get('work_key', '')
    subjects = request.form.get('subjects', '')
    
    # Check if book already exists
    existing = Book.query.filter_by(title=title, author=author).first()
    if existing:
        flash(f'Book "{title}" already exists!', 'warning')
        return redirect(url_for('admin.import_books'))
    
    # Download cover image if available
    image_filename = None
    if cover_id:
        image_filename = download_cover(cover_id, title)
    
    # Get description from Works API
    description = get_book_description(work_key) if work_key else ''
    if not description:
        description = f"A book by {author}"
    
    # Get all genres from the form (pre-computed during search)
    all_genres = request.form.get('all_genres', '')
    genres_list = [g.strip() for g in all_genres.split(',') if g.strip()] if all_genres else [category]
    
    # Create book with full metadata
    new_book = Book(
        title=title,
        author=author,
        price=price,
        stock=10,
        description=description,
        isbn=isbn,
        category=category,
        genres=','.join(genres_list),  # Store multiple genres
        image=image_filename
    )
    
    db.session.add(new_book)
    db.session.commit()
    
    flash(f'Successfully imported "{title}" with genres: {", ".join(genres_list)}!', 'success')
    return redirect(url_for('admin.import_books'))


# -------------------------------
# Add Book Manually
# -------------------------------
@admin_bp.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'GET':
        return render_template('admin/add_book.html')
    
    # POST - Add book
    title = request.form['title']
    author = request.form['author']
    price = request.form['price']
    stock = request.form['stock']
    description = request.form.get('description', '')
    isbn = request.form.get('isbn', '')
    category = request.form.get('category', 'General')

    # Handle image upload
    file = request.files.get('image')
    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    new_book = Book(
        title=title,
        author=author,
        price=price,
        stock=stock,
        description=description,
        isbn=isbn,
        category=category,
        image=filename
    )

    db.session.add(new_book)
    db.session.commit()

    # If no image uploaded, auto-assign one
    if not filename:
        new_book.image = auto_assign_image(new_book)
        db.session.commit()

    flash('Book added successfully!', 'success')
    return redirect(url_for('admin.add_book'))


# -------------------------------
# Delete All Books
# -------------------------------
@admin_bp.route('/delete-all-books', methods=['POST'])
def delete_all_books():
    """Delete all books from the database"""
    Book.query.delete()
    db.session.commit()
    flash('All books deleted!', 'success')
    return redirect(url_for('admin.dashboard'))


# -------------------------------
# Delete Single Book
# -------------------------------
@admin_bp.route('/delete-book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    """Delete a single book and remove it from all carts"""
    from app.models import Cart
    
    book = Book.query.get_or_404(book_id)
    title = book.title
    
    # First, delete all cart items containing this book
    Cart.query.filter_by(book_id=book_id).delete()
    
    # Now delete the book
    db.session.delete(book)
    db.session.commit()
    flash(f'Deleted "{title}"', 'success')
    return redirect(url_for('admin.manage_books'))


# -------------------------------
# Manage Books (List all books for admin)
# -------------------------------
@admin_bp.route('/books')
def manage_books():
    """List all books for management"""
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template('admin/manage_books.html', books=books)


# -------------------------------
# Fix Book Images (remove wrong calculus images)
# -------------------------------
@admin_bp.route('/fix-images', methods=['POST'])
def fix_images():
    """Fix books that have wrong images assigned"""
    # Clear images that don't match the book title
    books = Book.query.all()
    fixed = 0
    for book in books:
        if book.image and 'calculus' in book.image.lower():
            if 'calculus' not in book.title.lower():
                book.image = None
                fixed += 1
    db.session.commit()
    flash(f'Fixed {fixed} book images!', 'success')
    return redirect(url_for('admin.manage_books'))


# -------------------------------
# API: Verify Admin (for JS check)
# -------------------------------
@admin_bp.route('/verify', methods=['POST'])
@admin_api_required
def verify_admin():
    """API endpoint for JavaScript to verify admin status"""
    return jsonify({'status': 'ok', 'message': 'Admin verified'}), 200

