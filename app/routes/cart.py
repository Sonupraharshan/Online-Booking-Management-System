from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Cart, Book

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


# -------------------------------
# Add Book to Cart
# -------------------------------
@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    data = request.get_json()
    book_id = data.get('book_id')
    quantity = data.get('quantity', 1)

    if not book_id:
        return jsonify({'error': 'Book ID is required'}), 400

    user_id = int(get_jwt_identity())
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    cart_item = Cart.query.filter_by(user_id=user_id, book_id=book_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=user_id, book_id=book_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({'message': 'Book added to cart'}), 200


# -------------------------------
# Get all cart items (JSON)
# -------------------------------
@cart_bp.route('/', methods=['GET'])
@jwt_required()
def view_cart():
    user_id = int(get_jwt_identity())
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    result = []
    for item in cart_items:
        result.append({
            'cart_id': item.id,
            'book_id': item.book.id,
            'title': item.book.title,
            'author': item.book.author,
            'price': item.book.price,
            'quantity': item.quantity
        })

    return jsonify(result), 200


# -------------------------------
# Cart Page (HTML) - Public route
# -------------------------------
@cart_bp.route('/page')
def cart_page():
    return render_template('cart.html')
