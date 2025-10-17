from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from app import db
from app.models import Book
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Configure where images will be saved
UPLOAD_FOLDER = 'app/static/images/books'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = request.form['price']
        stock = request.form['stock']
        description = request.form.get('description', '')
        isbn = request.form.get('isbn', '')
        category = request.form.get('category', '')

        # Handle image upload
        file = request.files['image']
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
        db.session.commit()  # commit here
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin.add_book'))

    return render_template('admin/add_book.html')
