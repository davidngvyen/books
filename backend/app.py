from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import os

from auth.routes import auth_bp
from books.routes import books_bp
from orders.routes import orders_bp
from manager.routes import manager_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(manager_bp)
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Online Bookstore API',
            'version': '1.0',
            'endpoints': {
                'auth': '/api/auth/register, /api/auth/login',
                'books': '/api/books',
                'orders': '/api/orders',
                'manager': '/api/manager/orders, /api/manager/books'
            }
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Server running at: http://localhost:5000")
    print("API documentation: http://localhost:5000/")
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
