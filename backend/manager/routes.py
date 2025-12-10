from flask import Blueprint, request, jsonify
from auth.routes import role_required
from models import (
    get_all_orders, get_order_by_id, get_order_items,
    update_order_payment_status, create_book, update_book,
    get_all_books, get_all_books_for_manager, get_book_by_id
)
from cache import cache

manager_bp = Blueprint('manager', __name__, url_prefix='/api/manager')

@manager_bp.route('/orders', methods=['GET'])
@role_required('manager')
def get_orders():
    try:
        orders = get_all_orders()
        
        for order in orders:
            order['total_amount'] = float(order['total_amount'])
        
        return jsonify({
            'orders': orders,
            'count': len(orders)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve orders: {str(e)}'}), 500

@manager_bp.route('/orders/<int:order_id>', methods=['GET'])
@role_required('manager')
def get_order_details(order_id):
    try:
        order = get_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        items = get_order_items(order_id)
        
        order['total_amount'] = float(order['total_amount'])
        for item in items:
            item['price'] = float(item['price'])
        
        return jsonify({
            'order': order,
            'items': items
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve order: {str(e)}'}), 500

@manager_bp.route('/orders/<int:order_id>/payment-status', methods=['PATCH'])
@role_required('manager')
def update_payment_status(order_id):
    data = request.get_json()
    
    if not data or 'payment_status' not in data:
        return jsonify({'error': 'Missing payment_status field'}), 400
    
    payment_status = data['payment_status']
    
    allowed_statuses = ['Pending', 'Paid', 'Cancelled']
    if payment_status not in allowed_statuses:
        return jsonify({
            'error': f'Invalid payment status. Allowed values: {", ".join(allowed_statuses)}'
        }), 400
    
    order = get_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    try:
        update_order_payment_status(order_id, payment_status)
        
        return jsonify({
            'message': 'Payment status updated successfully',
            'order_id': order_id,
            'payment_status': payment_status
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update payment status: {str(e)}'}), 500

@manager_bp.route('/books', methods=['GET'])
@role_required('manager')
def get_all_books_manager():
    try:
        books = get_all_books_for_manager()
        
        for book in books:
            book['price_buy'] = float(book['price_buy'])
            book['price_rent'] = float(book['price_rent'])
        
        return jsonify({
            'books': books,
            'count': len(books)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve books: {str(e)}'}), 500

@manager_bp.route('/books', methods=['POST'])
@role_required('manager')
def add_book():
    data = request.get_json()
    
    required_fields = ['title', 'author', 'price_buy', 'price_rent']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': f'Missing required fields. Required: {", ".join(required_fields)}'}), 400
    
    title = data['title'].strip()
    author = data['author'].strip()
    
    try:
        price_buy = float(data['price_buy'])
        price_rent = float(data['price_rent'])
        
        if price_buy <= 0 or price_rent <= 0:
            return jsonify({'error': 'Prices must be greater than 0'}), 400
            
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid price format'}), 400
    
    if len(title) < 1 or len(author) < 1:
        return jsonify({'error': 'Title and author cannot be empty'}), 400
    
    try:
        book_id = create_book(title, author, price_buy, price_rent)
        
        cache.clear()
        
        return jsonify({
            'message': 'Book added successfully',
            'book_id': book_id,
            'title': title,
            'author': author
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to add book: {str(e)}'}), 500

@manager_bp.route('/books/<int:book_id>', methods=['PUT'])
@role_required('manager')
def edit_book(book_id):
    data = request.get_json()
    
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    required_fields = ['title', 'author', 'price_buy', 'price_rent', 'available']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': f'Missing required fields. Required: {", ".join(required_fields)}'}), 400
    
    title = data['title'].strip()
    author = data['author'].strip()
    available = bool(data['available'])
    
    try:
        price_buy = float(data['price_buy'])
        price_rent = float(data['price_rent'])
        
        if price_buy <= 0 or price_rent <= 0:
            return jsonify({'error': 'Prices must be greater than 0'}), 400
            
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid price format'}), 400
    
    if len(title) < 1 or len(author) < 1:
        return jsonify({'error': 'Title and author cannot be empty'}), 400
    
    try:
        update_book(book_id, title, author, price_buy, price_rent, available)
        
        cache.clear()
        
        return jsonify({
            'message': 'Book updated successfully',
            'book_id': book_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update book: {str(e)}'}), 500
