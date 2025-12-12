from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # user or admin

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    isbn = db.Column(db.String(50))
    category = db.Column(db.String(50))  # Primary category for filtering
    genres = db.Column(db.String(255))   # Multiple genres, comma-separated
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def genres_list(self):
        """Return genres as a list"""
        if not self.genres:
            return [self.category] if self.category else []
        return [g.strip() for g in self.genres.split(',') if g.strip()]
    
    def set_genres(self, genres_list):
        """Set genres from a list"""
        self.genres = ','.join(genres_list) if genres_list else ''

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    book = db.relationship('Book', backref=db.backref('cart_entries', lazy=True))
