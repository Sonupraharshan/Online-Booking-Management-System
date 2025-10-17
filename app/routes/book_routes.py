from flask import Blueprint, render_template
from app.models import Book

book_bp = Blueprint('books', __name__)

@book_bp.route('/books')
def list_books():
    books = Book.query.all()
    return render_template('books/list_books.html', books=books)

@book_bp.route('/book/<int:id>')
def book_details(id):
    book = Book.query.get_or_404(id)
    return render_template('books/book_details.html', book=book)
