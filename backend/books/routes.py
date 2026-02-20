from flask import Blueprint, request, jsonify
from auth.routes import login_required
from models import (
    get_all_books,
    search_books,
    get_book_by_id,
    get_all_categories,
    get_reviews_by_book,
    upsert_review
)
from cache import cache

books_bp = Blueprint('books', __name__, url_prefix='/api/books')

@books_bp.route('', methods=['GET'])
def get_books():
    keyword = request.args.get('q', '').strip()
    
    try:
        #check cache first
        cache_key = keyword
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
        
        cache.set(cache_key, books)
        
        return jsonify({
            'books': books,
            'count': len(books)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve books: {str(e)}'}), 500

@books_bp.route('/categories', methods=['GET'])
def list_categories():
    try:
        categories = get_all_categories()
        return jsonify({'categories': categories, 'count': len(categories)}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve categories: {str(e)}'}), 500

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

@books_bp.route('/<int:book_id>/reviews', methods=['GET'])
def get_book_reviews(book_id):
    try:
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404

        reviews = get_reviews_by_book(book_id)
        return jsonify({'reviews': reviews, 'count': len(reviews)}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve reviews: {str(e)}'}), 500

@books_bp.route('/<int:book_id>/reviews', methods=['POST'])
@login_required
def add_or_update_review(book_id):
    data = request.get_json()

    if not data or 'rating' not in data:
        return jsonify({'error': 'Missing rating field'}), 400

    try:
        rating = int(data['rating'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Rating must be an integer'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    review_text = (data.get('review_text') or '').strip() or None

    try:
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404

        upsert_review(book_id, request.user['user_id'], rating, review_text)
        return jsonify({'message': 'Review saved successfully'}), 201
    except Exception as e:
        return jsonify({'error': f'Failed to save review: {str(e)}'}), 500
