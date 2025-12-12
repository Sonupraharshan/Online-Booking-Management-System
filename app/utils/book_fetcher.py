"""
Book Fetcher Utility - Fetches books from Open Library API with full metadata
"""
import requests
import os
import random
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'app/static/images/books'

# Category mapping from Open Library subjects
CATEGORY_MAP = {
    'fiction': 'Fiction',
    'science fiction': 'Sci-Fi',
    'fantasy': 'Fantasy',
    'mystery': 'Mystery',
    'thriller': 'Thriller',
    'romance': 'Romance',
    'horror': 'Horror',
    'programming': 'Programming',
    'python': 'Programming',
    'javascript': 'Programming',
    'java': 'Programming',
    'computer': 'Technology',
    'technology': 'Technology',
    'science': 'Science',
    'history': 'History',
    'biography': 'Biography',
    'self-help': 'Self-Help',
    'business': 'Business',
    'philosophy': 'Philosophy',
    'psychology': 'Psychology',
    'children': 'Children',
    'young adult': 'Young Adult',
    'poetry': 'Poetry',
    'cooking': 'Cooking',
    'art': 'Art',
    'travel': 'Travel',
    'education': 'Education',
}

def get_category(subjects):
    """Map Open Library subjects to a single normalized category.
    
    Handles combined subjects like 'Fiction / Adventure' by splitting
    and matching the first recognizable category.
    """
    if not subjects:
        return 'General'
    
    # Priority order for specific genres (more specific first)
    PRIORITY_KEYWORDS = [
        ('science fiction', 'Sci-Fi'),
        ('sci-fi', 'Sci-Fi'),
        ('fantasy', 'Fantasy'),
        ('mystery', 'Mystery'),
        ('thriller', 'Thriller'),
        ('romance', 'Romance'),
        ('horror', 'Horror'),
        ('adventure', 'Adventure'),
        ('spiritual', 'Spiritual'),
        ('religious', 'Spiritual'),
        ('programming', 'Programming'),
        ('python', 'Programming'),
        ('javascript', 'Programming'),
        ('java', 'Programming'),
        ('computer', 'Technology'),
        ('technology', 'Technology'),
        ('biography', 'Biography'),
        ('memoir', 'Biography'),
        ('self-help', 'Self-Help'),
        ('self help', 'Self-Help'),
        ('business', 'Business'),
        ('philosophy', 'Philosophy'),
        ('philosophical', 'Philosophy'),
        ('psychology', 'Psychology'),
        ('children', 'Children'),
        ('young adult', 'Young Adult'),
        ('poetry', 'Poetry'),
        ('cooking', 'Cooking'),
        ('recipes', 'Cooking'),
        ('art', 'Art'),
        ('travel', 'Travel'),
        ('education', 'Education'),
        ('history', 'History'),
        ('historical', 'History'),
        ('science', 'Science'),
        ('novel', 'Fiction'),
        ('fiction', 'Fiction'),  # Generic fiction last
    ]
    
    # Combine all subjects into one searchable string
    all_subjects = ' '.join(subjects).lower()
    
    # Also split by common separators to check individual parts
    # e.g., "Fiction / Adventure" -> ["fiction", "adventure"]
    for sep in ['/', ',', '-', '&', 'and']:
        all_subjects = all_subjects.replace(sep, ' ')
    
    # Check for priority keywords in order
    for keyword, category in PRIORITY_KEYWORDS:
        if keyword in all_subjects:
            return category
    
    return 'General'


def get_all_genres(subjects):
    """Get ALL matching genres from subjects, not just the first one."""
    if not subjects:
        return ['General']
    
    GENRE_KEYWORDS = [
        ('science fiction', 'Sci-Fi'),
        ('sci-fi', 'Sci-Fi'),
        ('fantasy', 'Fantasy'),
        ('mystery', 'Mystery'),
        ('thriller', 'Thriller'),
        ('romance', 'Romance'),
        ('horror', 'Horror'),
        ('adventure', 'Adventure'),
        ('spiritual', 'Spiritual'),
        ('programming', 'Programming'),
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
        ('fiction', 'Fiction'),
    ]
    
    all_subjects = ' '.join(subjects).lower()
    for sep in ['/', ',', '-', '&', 'and']:
        all_subjects = all_subjects.replace(sep, ' ')
    
    # Find all matching genres (unique)
    found_genres = []
    for keyword, genre in GENRE_KEYWORDS:
        if keyword in all_subjects and genre not in found_genres:
            found_genres.append(genre)
    
    return found_genres if found_genres else ['General']


def generate_price(page_count=None):
    """Generate a realistic price based on page count or random."""
    if page_count and page_count > 0:
        # Base price on page count: ~$0.03 per page + base $5
        base = 5 + (page_count * 0.03)
        price = round(min(max(base, 8), 35), 2)
    else:
        # Random price between $8 and $25
        price = round(random.uniform(8, 25), 2)
    return price


def search_books(query, limit=20):
    """
    Search Open Library for books matching the query.
    Returns a list of book dictionaries with full metadata.
    """
    # Include subjects in the search fields
    url = f"https://openlibrary.org/search.json?q={query}&limit={limit}&fields=key,title,author_name,cover_i,isbn,first_publish_year,subject,number_of_pages_median"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        books = []
        for doc in data.get('docs', []):
            # Get the first author or 'Unknown'
            authors = doc.get('author_name', ['Unknown'])
            author = authors[0] if authors else 'Unknown'
            
            # Get cover ID if available
            cover_id = doc.get('cover_i')
            
            # Get ISBN if available
            isbns = doc.get('isbn', [])
            isbn = isbns[0] if isbns else ''
            
            # Get subjects (genres) - get more for better genre detection
            subjects = doc.get('subject', [])[:10]  # Get 10 subjects for better genre matching
            category = get_category(subjects)
            all_genres = get_all_genres(subjects)  # Get ALL matching genres
            
            # Get page count for pricing
            page_count = doc.get('number_of_pages_median')
            price = generate_price(page_count)
            
            # Get work key for fetching description later
            work_key = doc.get('key', '')
            
            book = {
                'title': doc.get('title', 'Unknown Title'),
                'author': author,
                'cover_id': cover_id,
                'cover_url': f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None,
                'isbn': isbn,
                'first_publish_year': doc.get('first_publish_year', 'N/A'),
                'subjects': subjects,
                'category': category,
                'all_genres': all_genres,  # Include all genres
                'price': price,
                'page_count': page_count,
                'work_key': work_key,
            }
            books.append(book)
        
        return books
    except Exception as e:
        print(f"Error fetching books: {e}")
        return []


def get_book_description(work_key):
    """
    Fetch full description from Open Library Works API.
    """
    if not work_key:
        return ""
    
    url = f"https://openlibrary.org{work_key}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        description = data.get('description', '')
        
        # Description can be a string or a dict with 'value' key
        if isinstance(description, dict):
            description = description.get('value', '')
        
        return description[:500] if description else ""  # Limit to 500 chars
    except Exception as e:
        print(f"Error fetching description: {e}")
        return ""


def download_cover(cover_id, title):
    """
    Download a book cover image from Open Library.
    Returns the filename if successful, None otherwise.
    """
    if not cover_id:
        return None
    
    url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Create safe filename from title
        safe_title = secure_filename(title.lower().replace(' ', '_')[:50])
        filename = f"{safe_title}_{cover_id}.jpg"
        
        # Ensure upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filename
    except Exception as e:
        print(f"Error downloading cover: {e}")
        return None
