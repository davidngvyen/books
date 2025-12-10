from flask import Blueprint, request, jsonify
from auth.routes import login_required
from models import (
    create_order, create_order_item, get_order_by_id, 
    get_order_items, get_book_by_id, get_user_by_id
)
from email_service import send_order_bill
from datetime import datetime

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@orders_bp.route('', methods=['POST'])
@login_required
def create_new_order():
    data = request.get_json()
    
    if not data or 'items' not in data or not data['items']:
        return jsonify({'error': 'No items provided'}), 400
    
    user_id = request.user['user_id']
    items = data['items']
    
    order_items = []
    total_amount = 0
    
    for item in items:
        if 'book_id' not in item or 'type' not in item:
            return jsonify({'error': 'Invalid item structure'}), 400
        
        book_id = item['book_id']
        item_type = item['type'].lower()
        
        if item_type not in ['buy', 'rent']:
            return jsonify({'error': f'Invalid item type: {item_type}. Must be "buy" or "rent"'}), 400
        
        book = get_book_by_id(book_id)
        if not book:
            return jsonify({'error': f'Book with ID {book_id} not found'}), 404
        
        if not book['available']:
            return jsonify({'error': f'Book "{book["title"]}" is not available'}), 400
        
        price = float(book['price_buy'] if item_type == 'buy' else book['price_rent'])
        total_amount += price
        
        order_items.append({
            'book_id': book_id,
            'title': book['title'],
            'author': book['author'],
            'type': item_type,
            'price': price
        })
    
    try:
        order_id = create_order(user_id, total_amount)
        
        for item in order_items:
            create_order_item(
                order_id,
                item['book_id'],
                item['type'],
                item['price']
            )
        
        user = get_user_by_id(user_id)
        
        order_data = {
            'order_id': order_id,
            'username': user['username'],
            'items': order_items,
            'total': total_amount,
            'payment_status': 'Pending',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        email_sent = send_order_bill(user['email'], order_data)
        
        return jsonify({
            'order_id': order_id,
            'items': order_items,
            'total_amount': total_amount,
            'payment_status': 'Pending',
            'email_sent': email_sent,
            'message': 'Order created successfully' + (' (email sent)' if email_sent else ' (email failed - check SMTP config)')
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create order: {str(e)}'}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    try:
        order = get_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        #users can only see their own orders
        if request.user['role'] != 'manager' and order['user_id'] != request.user['user_id']:
            return jsonify({'error': 'Access denied'}), 403
        
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
