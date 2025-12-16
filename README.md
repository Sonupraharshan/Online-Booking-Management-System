# 📚 Online Booking Management System

A modern, feature-rich book store management system built with Flask and MySQL. This web application allows users to browse, search, and purchase books, while administrators can manage inventory, import books from Open Library API, and track sales.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### For Users
- 🔐 **User Authentication**: Secure registration and login with JWT tokens
- 📖 **Book Browsing**: Browse books by categories and genres
- 🔍 **Advanced Search**: Search books by title, author, or ISBN
- 🛒 **Shopping Cart**: Add books to cart and manage quantities
- 📋 **Book Details**: View detailed information including description, author, price, and availability
- 🏷️ **Multiple Genres**: Books can have multiple genre tags for better discovery

### For Administrators
- 👨‍💼 **Admin Dashboard**: Comprehensive dashboard with book statistics
- ➕ **Manual Book Entry**: Add books manually with image upload
- 🌐 **Import from Open Library**: Search and import books from Open Library API with cover images
- 📊 **Inventory Management**: View, edit, and delete books
- 🏷️ **Category Management**: Organize books by categories and genres
- 🖼️ **Image Management**: Automatic image assignment and cover download
- 🔧 **Bulk Operations**: Import multiple books at once, delete all books

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: Flask-JWT-Extended
- **API Integration**: Open Library API for book data
- **Frontend**: HTML, CSS, JavaScript
- **Image Handling**: Pillow for cover downloads

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Sonupraharshan/Online-Booking-Management-System.git
cd Online-Booking-Management-System
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure MySQL Database

Create a MySQL database:
```sql
CREATE DATABASE bookstore_db;
```

Update the database configuration in `app/__init__.py` if needed:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/bookstore_db'
```

### 6. Initialize the Database
The database tables will be created automatically when you first run the application.

## 🎯 Usage

### Running the Application

Start the Flask development server:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Creating an Admin Account

Run the admin creation script:
```bash
python create_admin.py
```

Follow the prompts to create your admin account.

### Importing Books

You can import books in two ways:

**1. Via Web Interface:**
- Login as admin
- Navigate to Admin Dashboard → Import Books
- Search for books and import them

**2. Bulk Import (Command Line):**
```bash
python bulk_import_books.py
```

This will import approximately 100 books across various categories from Open Library.

## 📁 Project Structure

```
Online-Booking-Management-System/
├── app/
│   ├── __init__.py           # Flask app initialization
│   ├── models.py             # Database models (User, Book, Cart, Booking)
│   ├── config.py             # Configuration settings
│   ├── routes/               # Route handlers
│   │   ├── admin.py          # Admin routes
│   │   ├── auth.py           # Authentication routes
│   │   ├── cart.py           # Shopping cart routes
│   │   └── debug.py          # Debug routes
│   ├── utils/                # Utility functions
│   │   ├── book_fetcher.py   # Open Library API integration
│   │   └── image_assigner.py # Image assignment logic
│   └── static/               # Static files (CSS, JS, images)
├── templates/                # HTML templates
│   ├── home.html             # Homepage
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── cart.html             # Shopping cart
│   ├── book_detail.html      # Book details
│   └── admin/                # Admin templates
│       ├── dashboard.html
│       ├── add_book.html
│       ├── import_books.html
│       └── manage_books.html
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── bulk_import_books.py      # Bulk book import script
├── create_admin.py           # Admin account creation script
└── README.md                 # This file
```

## 🗄️ Database Models

### User
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password`: Hashed password
- `role`: User role (user/admin)

### Book
- `id`: Primary key
- `title`: Book title
- `author`: Book author
- `price`: Book price
- `stock`: Available quantity
- `description`: Book description
- `isbn`: ISBN number
- `category`: Primary category
- `genres`: Comma-separated genre tags
- `image`: Cover image filename
- `created_at`: Creation timestamp

### Cart
- `id`: Primary key
- `user_id`: Foreign key to User
- `book_id`: Foreign key to Book
- `quantity`: Number of items
- `added_at`: Timestamp

### Booking
- `id`: Primary key
- `user_id`: Foreign key to User
- `book_id`: Foreign key to Book
- `booked_at`: Booking timestamp

## 🔧 Utility Scripts

### fix_categories.py
Fixes book categories and genres in the database.

### add_genres_column.py
Migration script to add the genres column to existing books.

## 🌐 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login

### Books
- `GET /` - Homepage with book listings
- `GET /book/<id>` - Book details

### Cart
- `GET /cart` - View cart
- `POST /cart/add` - Add item to cart
- `POST /cart/update` - Update cart quantity
- `POST /cart/remove` - Remove item from cart

### Admin (Protected)
- `GET /admin` - Admin dashboard
- `GET /admin/add-book` - Add book form
- `POST /admin/add-book` - Create new book
- `GET /admin/import-books` - Import from Open Library
- `POST /admin/import-book` - Import single book
- `GET /admin/books` - Manage all books
- `POST /admin/delete-book/<id>` - Delete book
- `POST /admin/verify` - Verify admin status

## 🔒 Security Features

- JWT-based authentication with 7-day token expiration
- Password hashing (implementation recommended: use werkzeug.security)
- Admin-only route protection
- CORS enabled for API access
- SQL injection protection via SQLAlchemy ORM

## 🎨 Features in Detail

### Multiple Genre Support
Books can have multiple genres, making them discoverable across different categories. The system automatically extracts relevant genres from Open Library subjects during import.

### Open Library Integration
The system integrates with the Open Library API to:
- Search for books by title, author, or keyword
- Download high-quality cover images
- Import book descriptions and metadata
- Extract genre information from subjects

### Smart Image Management
- Automatic cover download from Open Library
- Manual image upload support
- Auto-assignment of existing images based on title/author
- Image format validation (PNG, JPG, JPEG, GIF)

## 📝 Configuration

Update `app/__init__.py` to configure:
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `JWT_ACCESS_TOKEN_EXPIRES`: Token expiration time

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Sonu Praharshan**
- GitHub: [@Sonupraharshan](https://github.com/Sonupraharshan)

## 🙏 Acknowledgments

- [Open Library API](https://openlibrary.org/developers/api) for book data
- Flask community for excellent documentation
- All contributors and users of this project

## 📞 Support

If you encounter any issues or have questions:
1. Check existing issues on GitHub
2. Create a new issue with detailed description
3. Provide error logs and steps to reproduce

---

**Happy Reading! 📚**