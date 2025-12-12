"""
Bulk Book Import Script
Imports approximately 100 books from Open Library API
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Book
from app.utils.book_fetcher import search_books, download_cover, get_book_description, get_all_genres
import time

# Search queries to get a variety of books across categories
SEARCH_QUERIES = [
    # Fiction & Classics
    ("harry potter", 8),
    ("lord of the rings", 6),
    ("game of thrones", 5),
    ("stephen king", 8),
    ("agatha christie", 6),
    
    # Sci-Fi & Fantasy
    ("dune herbert", 4),
    ("asimov foundation", 4),
    ("brandon sanderson", 5),
    
    # Thriller & Mystery
    ("dan brown", 5),
    ("john grisham", 5),
    ("sherlock holmes", 4),
    
    # Self-Help & Business
    ("atomic habits", 3),
    ("think and grow rich", 3),
    ("rich dad poor dad", 3),
    ("how to win friends", 3),
    
    # Programming & Technology
    ("python programming", 5),
    ("javascript web", 4),
    ("clean code", 4),
    ("algorithms", 4),
    
    # Biography & History
    ("steve jobs biography", 3),
    ("elon musk", 3),
    ("world war history", 4),
    
    # Romance & Drama
    ("nicholas sparks", 5),
    ("jane austen", 4),
    
    # Children & Young Adult
    ("percy jackson", 5),
    ("hunger games", 4),
    ("diary of a wimpy kid", 4),
]

def bulk_import():
    """Import books from multiple categories."""
    app = create_app()
    
    with app.app_context():
        total_imported = 0
        total_skipped = 0
        
        print("=" * 60)
        print("📚 BULK BOOK IMPORT STARTED")
        print("=" * 60)
        
        for query, limit in SEARCH_QUERIES:
            print(f"\n🔍 Searching: '{query}' (limit: {limit})")
            
            try:
                books = search_books(query, limit=limit)
                
                for book_data in books:
                    title = book_data['title']
                    author = book_data['author']
                    
                    # Check if already exists
                    existing = Book.query.filter_by(title=title, author=author).first()
                    if existing:
                        print(f"  ⏭️  Skipped (exists): {title[:40]}")
                        total_skipped += 1
                        continue
                    
                    # Download cover
                    image_filename = None
                    if book_data.get('cover_id'):
                        image_filename = download_cover(book_data['cover_id'], title)
                    
                    # Get description
                    description = ""
                    if book_data.get('work_key'):
                        description = get_book_description(book_data['work_key'])
                    if not description:
                        description = f"A book by {author}"
                    
                    # Get genres
                    all_genres = book_data.get('all_genres', [book_data.get('category', 'General')])
                    
                    # Create book
                    new_book = Book(
                        title=title,
                        author=author,
                        price=book_data.get('price', 12.99),
                        stock=10,
                        description=description,
                        isbn=book_data.get('isbn', ''),
                        category=book_data.get('category', 'General'),
                        genres=','.join(all_genres),
                        image=image_filename
                    )
                    
                    db.session.add(new_book)
                    db.session.commit()
                    
                    total_imported += 1
                    print(f"  ✅ Imported: {title[:40]} ({new_book.category})")
                    
                    # Small delay to be nice to the API
                    time.sleep(0.3)
                    
            except Exception as e:
                print(f"  ❌ Error with query '{query}': {e}")
                continue
        
        print("\n" + "=" * 60)
        print(f"📊 IMPORT COMPLETE!")
        print(f"   ✅ Imported: {total_imported} books")
        print(f"   ⏭️  Skipped: {total_skipped} books (already existed)")
        print(f"   📚 Total in database: {Book.query.count()} books")
        print("=" * 60)


if __name__ == '__main__':
    bulk_import()
