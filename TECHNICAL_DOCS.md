# Technical Documentation - Online Bookstore

## 1. Architecture Overview

### 1.1 System Architecture

The Online Bookstore is a three-tier application:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│                 (Python Tkinter Desktop App)                 │
│                                                              │
│  - Login/Registration UI                                    │
│  - Customer Shopping Interface                              │
│  - Manager Administration Interface                         │
└──────────────────┬───────────────────────────────────────────┘
                   │ HTTP/REST (JSON)
                   │ Authentication: JWT Tokens
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                    (Flask REST API)                          │
│                                                              │
│  - Authentication & Authorization                           │
│  - Business Logic                                           │
│  - Input Validation                                         │
│  - Email Service                                            │
└──────────────────┬───────────────────────────────────────────┘
                   │ SQL Queries
                   │ Connection Pooling
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│                     (MySQL Database)                         │
│                                                              │
│  - User Data (with hashed passwords)                        │
│  - Book Catalog                                             │
│  - Orders & Transactions                                    │
│  - Relational Integrity with Foreign Keys                  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

**Backend:**
- **Flask 3.0**: Lightweight Python web framework
- **PyJWT 2.8**: JSON Web Token authentication
- **bcrypt 4.1**: Password hashing
- **MySQL Connector**: Database driver
- **Python SMTP**: Email sending

**Desktop Client:**
- **Tkinter**: Python's standard GUI library (cross-platform)
- **requests**: HTTP client library
- **threading**: Async operations to prevent UI freezing

**Database:**
- **MySQL 5.7+/8.0+**: Relational database
- **InnoDB Engine**: Transaction support and foreign keys

### 1.3 Design Principles

1. **RESTful API**: Clear, resource-based endpoints
2. **Separation of Concerns**: Distinct layers for UI, logic, and data
3. **Stateless Authentication**: JWT tokens (no server-side sessions)
4. **Role-Based Access Control**: Customer vs Manager permissions
5. **Input Validation**: All user inputs validated before processing

---

## 2. Database Design

### 2.1 Entity Relationship Diagram

```
┌─────────────┐
│    users    │
├─────────────┤
│ id (PK)     │───┐
│ username    │   │
│ email       │   │
│ password_hash│  │
│ role        │   │
└─────────────┘   │
                  │
                  │ 1
                  │
                  │
                  │ N
┌─────────────┐   │
│   orders    │◄──┘
├─────────────┤
│ id (PK)     │───┐
│ user_id (FK)│   │
│ total_amount│   │
│ payment_status  │
│ created_at  │   │
└─────────────┘   │
                  │ 1
                  │
                  │
                  │ N
┌─────────────┐   │        ┌─────────────┐
│ order_items │◄──┘        │    books    │
├─────────────┤            ├─────────────┤
│ id (PK)     │         ┌─►│ id (PK)     │
│ order_id(FK)│         │  │ title       │
│ book_id (FK)├─────────┘  │ author      │
│ item_type   │            │ price_buy   │
│ price       │            │ price_rent  │
└─────────────┘            │ available   │
                           └─────────────┘
```

### 2.2 Table Details

#### users
- **Purpose**: Store customer and manager accounts
- **Key Fields**:
  - `role`: ENUM('customer', 'manager') - determines access level
  - `password_hash`: bcrypt hashed password (never store plain text)
- **Indexes**:
  - Primary key on `id`
  - Unique indexes on `username` and `email`
  - Index on `role` for filtering

#### books
- **Purpose**: Store book catalog
- **Key Fields**:
  - `price_buy`: Decimal(10,2) - purchase price
  - `price_rent`: Decimal(10,2) - rental price
  - `available`: Boolean - controls customer visibility
- **Indexes**:
  - Primary key on `id`
  - Indexes on `title` and `author` for fast searching

#### orders
- **Purpose**: Store customer orders
- **Key Fields**:
  - `user_id`: Foreign key to users table
  - `total_amount`: Calculated sum of all items
  - `payment_status`: ENUM('Pending', 'Paid', 'Cancelled')
- **Indexes**:
  - Primary key on `id`
  - Index on `user_id` for user's order history
  - Index on `payment_status` for manager filtering

#### order_items
- **Purpose**: Many-to-many relationship between orders and books
- **Key Fields**:
  - `item_type`: ENUM('buy', 'rent') - transaction type
  - `price`: Captured at order time (historical pricing)
- **Why capture price?**: Preserves order history even if book prices change later

### 2.3 Data Integrity

- **Foreign Keys**: Enforce referential integrity
  - `orders.user_id → users.id`
  - `order_items.order_id → orders.id`
  - `order_items.book_id → books.id`
- **ON DELETE CASCADE**: When order deleted, items are also deleted
- **Transaction Support**: InnoDB engine ensures ACID properties

---

## 3. Backend API Design

### 3.1 Authentication Flow

```
┌─────────────┐                          ┌─────────────┐
│   Client    │                          │   Server    │
└──────┬──────┘                          └──────┬──────┘
       │                                        │
       │  POST /api/auth/register               │
       ├───────────────────────────────────────►│
       │  {username, email, password}           │
       │                                        │
       │                                        │ Hash password
       │                                        │ Store user
       │                                        │
       │  201 Created                           │
       │◄───────────────────────────────────────┤
       │  {user_id, username}                   │
       │                                        │
       │  POST /api/auth/login                  │
       ├───────────────────────────────────────►│
       │  {username, password}                  │
       │                                        │
       │                                        │ Verify password
       │                                        │ Generate JWT
       │                                        │
       │  200 OK                                │
       │◄───────────────────────────────────────┤
       │  {token, user{id, role, ...}}          │
       │                                        │
       │  GET /api/books                        │
       ├───────────────────────────────────────►│
       │  Authorization: Bearer <token>         │
       │                                        │
       │                                        │ Verify JWT
       │                                        │ Extract user_id
       │                                        │ Query DB
       │                                        │
       │  200 OK                                │
       │◄───────────────────────────────────────┤
       │  {books: [...]}                        │
```

### 3.2 JWT Token Structure

**Payload:**
```json
{
  "user_id": 1,
  "username": "alice",
  "role": "customer",
  "exp": 1704153600
}
```

**How it works:**
1. Server signs token with SECRET_KEY
2. Client stores token in memory
3. Client includes token in Authorization header for all requests
4. Server verifies signature and checks expiration
5. Server extracts user info from token (no DB lookup needed)

**Security:**
- Token expires after 24 hours (configurable)
- Signature prevents tampering
- If SECRET_KEY changes, all tokens become invalid

### 3.3 Authorization Decorators

**@login_required:**
```python
def login_required(f):
    """Ensures user is authenticated"""
    # 1. Extract token from Authorization header
    # 2. Verify JWT signature
    # 3. Check expiration
    # 4. Attach user info to request
```

**@role_required('manager'):**
```python
def role_required(required_role):
    """Ensures user has specific role"""
    # 1. First calls @login_required
    # 2. Checks if user.role matches required_role
    # 3. Returns 403 Forbidden if role mismatch
```

### 3.4 Input Validation

**Example: Create Order**
```python
def create_new_order():
    # 1. Validate JSON structure
    if 'items' not in data:
        return error(400, "Missing items")
    
    # 2. Validate each item
    for item in items:
        if 'book_id' not in item or 'type' not in item:
            return error(400, "Invalid item")
        
        # 3. Validate enum values
        if item['type'] not in ['buy', 'rent']:
            return error(400, "Invalid type")
        
        # 4. Verify book exists
        book = get_book_by_id(item['book_id'])
        if not book:
            return error(404, "Book not found")
        
        # 5. Check availability
        if not book['available']:
            return error(400, "Book unavailable")
    
    # 6. Create order in transaction
    # ...
```

---

## 4. Security Implementation

### 4.1 Password Security

**Hashing with bcrypt:**
```python
import bcrypt

# Registration
password = "password123"
salt = bcrypt.gensalt()
password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
# Result: $2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy

# Login verification
if bcrypt.checkpw(password.encode('utf-8'), password_hash):
    # Password correct
```

**Why bcrypt?**
- **Adaptive**: Cost factor can be increased as computers get faster
- **Salt included**: Each password has unique hash
- **Slow by design**: Prevents brute force attacks
- **Industry standard**: Well-tested and trusted

### 4.2 SQL Injection Prevention

**Bad (vulnerable):**
```python
query = f"SELECT * FROM users WHERE username = '{username}'"
```

**Good (safe):**
```python
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))
```

**All queries use prepared statements:**
- User input treated as data, not code
- Special characters properly escaped
- Prevents malicious SQL injection

### 4.3 Cross-Origin Resource Sharing (CORS)

```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

**Purpose:**
- Allows desktop client to make HTTP requests to backend
- In production, restrict to specific origins
- Prevents unauthorized web apps from accessing API

### 4.4 Role-Based Access Control

**Customer Restrictions:**
-  Can search books
-  Can place orders
-  Can view own orders only
-  Cannot view other users' orders
-  Cannot access manager endpoints

**Manager Abilities:**
-  Can view all orders
-  Can update payment status
-  Can add/edit books
-  Can view all users' data

**Implementation:**
```python
# In get_order endpoint
if request.user['role'] != 'manager' and order['user_id'] != request.user['user_id']:
    return error(403, "Access denied")
```

### 4.5 Error Handling

**Sensitive Information Not Leaked:**
```python
# Bad
except Exception as e:
    return error(500, str(e))  # Might expose DB details

# Good
except Exception as e:
    logger.error(f"Order creation failed: {e}")  # Log for debugging
    return error(500, "Failed to create order")  # Generic message
```

---

## 5. Performance Optimization

### 5.1 Database Indexes

**Created indexes:**
```sql
-- Fast username lookup
INDEX idx_username ON users(username)

-- Fast book search
INDEX idx_title ON books(title)
INDEX idx_author ON books(author)

-- Fast order queries
INDEX idx_user_id ON orders(user_id)
INDEX idx_payment_status ON orders(payment_status)
```

**Impact:**
- Username lookup: O(log n) instead of O(n)
- Book search: Dramatically faster for large catalogs
- Order filtering: Quick manager queries

### 5.2 Query Optimization

**Efficient joins:**
```sql
-- Get orders with user info in single query
SELECT o.*, u.username, u.email 
FROM orders o
JOIN users u ON o.user_id = u.id
ORDER BY o.created_at DESC
```

**Avoid N+1 queries:**
- Fetch order items in separate query, not per-order
- Desktop client batches requests when possible

### 5.3 Connection Management

**MySQL Connector handles:**
- Connection pooling (reuse connections)
- Automatic reconnection on failure
- Timeout handling

**Per-request pattern:**
```python
def execute_query(...):
    conn = get_db_connection()  # Get from pool
    try:
        # Execute query
    finally:
        conn.close()  # Return to pool
```

### 5.4 Response Times

**Target: < 500ms for all endpoints**

Typical response times:
- Login: ~100-200ms (bcrypt verification)
- Search books: ~50-100ms (indexed query)
- Create order: ~100-200ms (transaction + email)
- Get orders: ~50-100ms (simple join)

---

## 6. Desktop Client Architecture

### 6.1 Threading for Async Operations

**Why threading?**
- Tkinter is single-threaded
- Network requests can take 100ms+
- UI freezes without async handling

**Pattern:**
```python
def search_books(self):
    # Disable button, show loading
    self.button.config(state='disabled')
    self.status.config(text="Loading...")
    
    # Run in background thread
    def search_thread():
        success, data = self.api_client.search_books(keyword)
        
        # Update UI in main thread
        self.after(0, lambda: self.handle_response(success, data))
    
    threading.Thread(target=search_thread, daemon=True).start()
```

**Benefits:**
- UI remains responsive
- User can cancel operations
- Loading indicators possible

### 6.2 API Client Abstraction

**Purpose:**
- Single place for all HTTP logic
- Error handling centralized
- Easy to change backend URL

**Pattern:**
```python
class APIClient:
    def search_books(self, keyword):
        try:
            response = requests.get(...)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, "Error message"
        except requests.ConnectionError:
            return False, "Cannot connect to server"
```

**All views use APIClient, never raw requests**

### 6.3 View Separation

**login_view.py:**
- Handles registration and login forms
- Calls callback on success: `on_login_success()`

**customer_main.py:**
- Search and browse books
- Shopping cart management
- Order placement

**manager_main.py:**
- Two tabs: Orders and Books
- CRUD operations on both
- Role-specific features

**Benefits:**
- Each view is self-contained
- Easy to maintain and test
- Can add new views without affecting others

---

## 7. Email Service

### 7.1 SMTP Configuration

**Supported providers:**
- Gmail (smtp.gmail.com:587)
- Outlook (smtp-mail.outlook.com:587)
- Any standard SMTP server

**Gmail setup:**
1. Enable 2FA on Google account
2. Generate app-specific password
3. Use app password in SMTP_PASSWORD

### 7.2 Bill Generation

**Template:**
```
╔══════════════════════════════════════════════════════════╗
║           ONLINE BOOKSTORE - ORDER RECEIPT               ║
╚══════════════════════════════════════════════════════════╝

Order ID: #123
Customer: alice
Date: 2024-01-01 12:00:00

──────────────────────────────────────────────────────────

ORDER ITEMS:

1. To Kill a Mockingbird by Harper Lee
   Type: BUY
   Price: $14.99

2. 1984 by George Orwell
   Type: RENT
   Price: $3.49

──────────────────────────────────────────────────────────

TOTAL AMOUNT: $18.48
Payment Status: Pending
```

### 7.3 Error Handling

**Email sending is optional:**
- Order succeeds even if email fails
- Error logged for debugging
- User informed of email status
- System continues functioning without SMTP

---

## 8. Testing

### 8.1 Backend Tests (pytest)

**Test categories:**
1. **Authentication**: Register, login, token validation
2. **Books**: Search, get all, get by ID
3. **Orders**: Create, authorization checks
4. **Manager**: Orders management, book CRUD, role checks

**Running tests:**
```bash
cd backend
pytest tests/test_api.py -v
```

### 8.2 Manual Testing Checklist

**Customer Flow:**
- [ ] Register new account
- [ ] Login with correct credentials
- [ ] Login fails with wrong password
- [ ] Search books by keyword
- [ ] Add books to cart (buy and rent)
- [ ] Remove items from cart
- [ ] Place order with multiple items
- [ ] Verify order email received
- [ ] Cannot access manager endpoints

**Manager Flow:**
- [ ] Login with manager credentials
- [ ] View all customer orders
- [ ] View order details
- [ ] Update payment status
- [ ] Add new book
- [ ] Edit existing book
- [ ] Toggle book availability
- [ ] Verify customer sees/doesn't see unavailable books

---

## 9. Deployment Considerations

### 9.1 Production Checklist

**Backend:**
- [ ] Change SECRET_KEY and JWT_SECRET
- [ ] Set DEBUG=False
- [ ] Use production MySQL credentials
- [ ] Configure proper CORS origins
- [ ] Set up SSL/HTTPS
- [ ] Use production SMTP credentials
- [ ] Set up logging
- [ ] Configure firewall

**Database:**
- [ ] Regular backups
- [ ] Monitor disk space
- [ ] Tune MySQL configuration
- [ ] Set up replication (optional)

**Desktop Client:**
- [ ] Update API base URL
- [ ] Package as executable (PyInstaller)
- [ ] Include requirements
- [ ] Test on target OS

### 9.2 Scalability

**Current limitations:**
- Single Flask process (not load-balanced)
- Single MySQL server

**Scaling options:**
1. **Horizontal scaling**: Multiple Flask instances with load balancer
2. **Database replication**: Master-slave for read queries
3. **Caching**: Redis for frequently accessed data
4. **CDN**: For static assets (if web version added)

---

## 10. Future Enhancements (v2.0+)

**NOT implemented in v1.0:**
-  Order history page for customers
-  Book reviews and ratings
-  Advanced search filters (genre, year, price range)
-  Inventory management
-  Rental return workflow
-  Payment gateway integration
-  Admin analytics dashboard
-  Password reset functionality
-  User profile editing
-  Book cover images

---

## Conclusion

This Online Bookstore demonstrates:

 **Clean Architecture**: Three-tier separation
 **Security Best Practices**: Hashing, JWT, input validation
 **RESTful Design**: Resource-based, stateless API
 **Role-Based Access**: Customer vs Manager permissions
 **Database Design**: Normalized schema with proper relationships
 **Performance**: Indexed queries, efficient joins
 **User Experience**: Responsive desktop GUI with async operations
 **Maintainability**: Modular code, clear separation of concerns

The system is production-ready for small to medium deployments and provides a solid foundation for future enhancements.
