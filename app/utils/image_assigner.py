import os
from app.models import Book
from app import db

def assign_images():
    """
    Auto-assign images to books that don't have one yet.
    Only assigns if image filename matches book title or author.
    Does NOT use fallback images to avoid wrong assignments.
    """
    images_path = os.path.join(os.path.dirname(__file__), "..", "static", "images", "books")
    images_path = os.path.abspath(images_path)

    if not os.path.exists(images_path):
        print("⚠️ No images folder found.")
        return

    images = os.listdir(images_path)
    books = Book.query.filter(Book.image == None).all()  # Only books without images

    assigned = 0
    for book in books:
        for img in images:
            # Match by title or author's first name
            title_match = book.title.lower().replace(" ", "_") in img.lower()
            author_first = book.author.lower().split()[0] if book.author else ""
            author_match = len(author_first) > 3 and author_first in img.lower()
            
            if title_match or author_match:
                book.image = img
                assigned += 1
                break
        # No fallback - leave image as None if no match

    db.session.commit()
    print(f"✅ Images auto-assigned to {assigned} books.")

