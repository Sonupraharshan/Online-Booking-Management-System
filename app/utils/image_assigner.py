import os
from app.models import Book
from app import db

def assign_images():
    images_path = os.path.join(os.path.dirname(__file__), "..", "static", "images", "books")
    images_path = os.path.abspath(images_path)

    if not os.path.exists(images_path):
        print("⚠️ No images folder found.")
        return

    images = os.listdir(images_path)
    books = Book.query.all()

    for book in books:
        matched = False
        for img in images:
            if (
                book.title.lower().replace(" ", "_") in img.lower()
                or book.author.lower().split()[0] in img.lower()
            ):
                book.image = img
                matched = True
                break

        if not matched and images:
            book.image = images[0]  # fallback image

    db.session.commit()
    print("✅ Images auto-assigned to books.")
