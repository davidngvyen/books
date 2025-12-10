from db import execute_query

#user functions
def create_user(username, email, password_hash, role='customer'):
    query = """
        INSERT INTO users (username, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(query, (username, email, password_hash, role), commit=True)

def get_user_by_username(username):
    query = "SELECT * FROM users WHERE username = %s"
    return execute_query(query, (username,), fetch_one=True)

def get_user_by_email(email):
    query = "SELECT * FROM users WHERE email = %s"
    return execute_query(query, (email,), fetch_one=True)

def get_user_by_id(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return execute_query(query, (user_id,), fetch_one=True)

#book functions
def get_all_books():
    query = "SELECT * FROM books WHERE available = TRUE ORDER BY title"
    return execute_query(query, fetch_all=True)

def get_all_books_for_manager():
    #gets all books even unavailable
    query = "SELECT * FROM books ORDER BY title"
    return execute_query(query, fetch_all=True)

def search_books(keyword):
    query = """
        SELECT * FROM books 
        WHERE available = TRUE 
        AND (title LIKE %s OR author LIKE %s)
        ORDER BY title
    """
    search_term = f"%{keyword}%"
    return execute_query(query, (search_term, search_term), fetch_all=True)

def get_book_by_id(book_id):
    query = "SELECT * FROM books WHERE id = %s"
    return execute_query(query, (book_id,), fetch_one=True)

def create_book(title, author, price_buy, price_rent):
    query = """
        INSERT INTO books (title, author, price_buy, price_rent)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(query, (title, author, price_buy, price_rent), commit=True)

def update_book(book_id, title, author, price_buy, price_rent, available):
    query = """
        UPDATE books 
        SET title = %s, author = %s, price_buy = %s, price_rent = %s, available = %s
        WHERE id = %s
    """
    return execute_query(query, (title, author, price_buy, price_rent, available, book_id), commit=True)

#order functions
def create_order(user_id, total_amount):
    query = """
        INSERT INTO orders (user_id, total_amount)
        VALUES (%s, %s)
    """
    return execute_query(query, (user_id, total_amount), commit=True)

def create_order_item(order_id, book_id, item_type, price):
    query = """
        INSERT INTO order_items (order_id, book_id, item_type, price)
        VALUES (%s, %s, %s, %s)
    """
    return execute_query(query, (order_id, book_id, item_type, price), commit=True)

def get_order_by_id(order_id):
    query = """
        SELECT o.*, u.username, u.email 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.id = %s
    """
    return execute_query(query, (order_id,), fetch_one=True)

def get_order_items(order_id):
    query = """
        SELECT oi.*, b.title, b.author
        FROM order_items oi
        JOIN books b ON oi.book_id = b.id
        WHERE oi.order_id = %s
    """
    return execute_query(query, (order_id,), fetch_all=True)

def get_all_orders():
    query = """
        SELECT o.*, u.username, u.email 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    """
    return execute_query(query, fetch_all=True)

def update_order_payment_status(order_id, payment_status):
    query = "UPDATE orders SET payment_status = %s WHERE id = %s"
    return execute_query(query, (payment_status, order_id), commit=True)
