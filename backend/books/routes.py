from flask import Blueprint, request, jsonify
from models import get_all_books, search_books, get_book_by_id
from cache import cache

books_bp = Blueprint('books', __name__, url_prefix='/api/books')

@books_bp.route('', methods=['GET'])
def get_books():
    keyword = request.args.get('q', '').strip()
    
    try:
        #check cache first
        cache_key = f"books:{keyword}"
        cached_books = cache.get(cache_key)
        
        if cached_books is not None:
            return jsonify({
                'books': cached_books,
                'count': len(cached_books),
                'cached': True
            }), 200
        
        #get from db
        if keyword:
            books = search_books(keyword)
        else:
            books = get_all_books()
        
        #convert decimal to float
        for book in books:
            book['price_buy'] = float(book['price_buy'])
            book['price_rent'] = float(book['price_rent'])
        
        cache.set(cache_key, books, ttl_seconds=30)
        
        return jsonify({
            'books': books,
            'count': len(books)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve books: {str(e)}'}), 500

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    try:
        book = get_book_by_id(book_id)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        book['price_buy'] = float(book['price_buy'])
        book['price_rent'] = float(book['price_rent'])
        
        return jsonify(book), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve book: {str(e)}'}), 500
