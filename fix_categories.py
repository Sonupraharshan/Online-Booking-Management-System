"""
Utility script to normalize all book categories in the database.
Run this from the project root: python fix_categories.py
"""
from app import create_app, db
from app.models import Book

# Priority order for specific genres (more specific first)
PRIORITY_KEYWORDS = [
    ('science fiction', 'Sci-Fi'),
    ('sci-fi', 'Sci-Fi'),
    ('fantasy', 'Fantasy'),
    ('mystery', 'Mystery'),
    ('thriller', 'Thriller'),
    ('romance', 'Romance'),
    ('horror', 'Horror'),
    ('programming', 'Programming'),
    ('python', 'Programming'),
    ('javascript', 'Programming'),
    ('java', 'Programming'),
    ('computer', 'Technology'),
    ('technology', 'Technology'),
    ('biography', 'Biography'),
    ('self-help', 'Self-Help'),
    ('business', 'Business'),
    ('philosophy', 'Philosophy'),
    ('psychology', 'Psychology'),
    ('children', 'Children'),
    ('young adult', 'Young Adult'),
    ('poetry', 'Poetry'),
    ('cooking', 'Cooking'),
    ('art', 'Art'),
    ('travel', 'Travel'),
    ('education', 'Education'),
    ('history', 'History'),
    ('science', 'Science'),
    ('fiction', 'Fiction'),  # Generic fiction last
]

def normalize_category(category):
    """Normalize a category to a standard one."""
    if not category:
        return 'General'
    
    cat_lower = category.lower()
    
    # Split by common separators
    for sep in ['/', ',', '-', '&', 'and']:
        cat_lower = cat_lower.replace(sep, ' ')
    
    # Check for priority keywords in order
    for keyword, new_category in PRIORITY_KEYWORDS:
        if keyword in cat_lower:
            return new_category
    
    return 'General'

def fix_categories():
    app = create_app()
    with app.app_context():
        books = Book.query.all()
        
        print(f"Found {len(books)} books to check.")
        updated = 0
        
        for book in books:
            old_category = book.category
            new_category = normalize_category(old_category)
            
            if old_category != new_category:
                print(f"'{book.title}': '{old_category}' -> '{new_category}'")
                book.category = new_category
                updated += 1
        
        db.session.commit()
        print(f"\nUpdated {updated} book categories.")

if __name__ == '__main__':
    fix_categories()
