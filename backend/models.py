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
        AND (title LIKE %s OR author LIKE %s OR isbn LIKE %s)
        ORDER BY title
    """
    search_term = f"%{keyword}%"
    return execute_query(query, (search_term, search_term, search_term), fetch_all=True)

def get_book_by_id(book_id):
    query = "SELECT * FROM books WHERE id = %s"
    return execute_query(query, (book_id,), fetch_one=True)

def create_book(isbn, title, author, price_buy, price_rent):
    query = """
        INSERT INTO books (isbn, title, author, price_buy, price_rent)
        VALUES (%s, %s, %s, %s, %s)
    """
    return execute_query(query, (isbn, title, author, price_buy, price_rent), commit=True)

def update_book(book_id, isbn, title, author, price_buy, price_rent, available):
    query = """
        UPDATE books 
        SET isbn = %s, title = %s, author = %s, price_buy = %s, price_rent = %s, available = %s
        WHERE id = %s
    """
    return execute_query(query, (isbn, title, author, price_buy, price_rent, available, book_id), commit=True)

def get_all_categories():
    query = "SELECT * FROM categories ORDER BY name"
    return execute_query(query, fetch_all=True)

def create_category(name):
    query = "INSERT INTO categories (name) VALUES (%s)"
    return execute_query(query, (name,), commit=True)

def get_book_categories(book_id):
    query = """
        SELECT c.id, c.name
        FROM categories c
        JOIN book_categories bc ON bc.category_id = c.id
        WHERE bc.book_id = %s
        ORDER BY c.name
    """
    return execute_query(query, (book_id,), fetch_all=True)

def replace_book_categories(book_id, category_ids):
    delete_query = "DELETE FROM book_categories WHERE book_id = %s"
    execute_query(delete_query, (book_id,), commit=True)

    if not category_ids:
        return 0

    insert_query = "INSERT INTO book_categories (book_id, category_id) VALUES (%s, %s)"
    count = 0
    for category_id in category_ids:
        execute_query(insert_query, (book_id, category_id), commit=True)
        count += 1
    return count

def get_reviews_by_book(book_id):
    query = """
        SELECT r.id, r.book_id, r.user_id, u.username, r.rating, r.review_text, r.created_at
        FROM reviews r
        JOIN users u ON u.id = r.user_id
        WHERE r.book_id = %s
        ORDER BY r.created_at DESC
    """
    return execute_query(query, (book_id,), fetch_all=True)

def upsert_review(book_id, user_id, rating, review_text):
    query = """
        INSERT INTO reviews (book_id, user_id, rating, review_text)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE rating = VALUES(rating), review_text = VALUES(review_text)
    """
    return execute_query(query, (book_id, user_id, rating, review_text), commit=True)

def get_user_addresses(user_id):
    query = "SELECT * FROM addresses WHERE user_id = %s ORDER BY is_default DESC, created_at DESC"
    return execute_query(query, (user_id,), fetch_all=True)

def get_address_for_user(address_id, user_id):
    query = "SELECT * FROM addresses WHERE id = %s AND user_id = %s"
    return execute_query(query, (address_id, user_id), fetch_one=True)

def create_address(user_id, full_name, phone, line1, line2, city, state, postal_code, country='USA', is_default=False):
    if is_default:
        reset_query = "UPDATE addresses SET is_default = FALSE WHERE user_id = %s"
        execute_query(reset_query, (user_id,), commit=True)

    query = """
        INSERT INTO addresses (user_id, full_name, phone, line1, line2, city, state, postal_code, country, is_default)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(
        query,
        (user_id, full_name, phone, line1, line2, city, state, postal_code, country, is_default),
        commit=True
    )

#order functions
def create_order(customer_id, total_amount, address_id=None):
    query = """
        INSERT INTO orders (customer_id, address_id, total_amount)
        VALUES (%s, %s, %s)
    """
    return execute_query(query, (customer_id, address_id, total_amount), commit=True)

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
        JOIN users u ON o.customer_id = u.id
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
        JOIN users u ON o.customer_id = u.id
        ORDER BY o.created_at DESC
    """
    return execute_query(query, fetch_all=True)

def update_order_payment_status(order_id, payment_status):
    query = "UPDATE orders SET payment_status = %s WHERE id = %s"
    return execute_query(query, (payment_status, order_id), commit=True)
