from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import abort
from app import db
from app.models import Book
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Configure where images will be saved
UPLOAD_FOLDER = 'app/static/images/books'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def auto_assign_image(book):
    """
    Assign an image automatically if none is uploaded.
    Matches by title or author name; otherwise, uses the first image.
    """
    images_path = os.path.join(os.getcwd(), UPLOAD_FOLDER)
    images = os.listdir(images_path) if os.path.exists(images_path) else []

    for img in images:
        if book.title.lower().replace(" ", "_") in img.lower() or book.author.lower().split()[0] in img.lower():
            return img

    return images[0] if images else None

@admin_bp.route('/add-book', methods=['GET', 'POST'])
@jwt_required()
def add_book():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        abort(403)
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = request.form['price']
        stock = request.form['stock']
        description = request.form.get('description', '')
        isbn = request.form.get('isbn', '')
        category = request.form.get('category', '')

        # Handle image upload
        file = request.files.get('image')
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
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
        db.session.commit()  # commit new book first to get ID

        # If no image uploaded, auto-assign one
        if not filename:
            new_book.image = auto_assign_image(new_book)
            db.session.commit()

        flash('Book added successfully!', 'success')
        return redirect(url_for('admin.add_book'))

    return render_template('admin/add_book.html')
