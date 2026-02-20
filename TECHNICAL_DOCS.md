# Technical Documentation - Online Bookstore (Updated)

## 1. Architecture Overview

### 1.1 System Architecture

The system is a 3-layer application:

- **Presentation Layer**: Tkinter desktop client (`desktop_client/`)
- **Application Layer**: Flask REST API (`backend/`)
- **Data Layer**: MySQL with normalized relational schema (`database/`)

Request flow:
1. Desktop client sends HTTP JSON requests.
2. Flask validates JWT + role rules.
3. Flask uses model functions with parameterized SQL.
4. DB access goes through PyMySQL connection pool.
5. Results returned as JSON.

### 1.2 Technology Stack

**Backend**
- Flask
- PyJWT
- bcrypt
- PyMySQL
- python-dotenv
- flask-cors

**Desktop Client**
- Tkinter
- requests
- threading

**Database**
- MySQL (InnoDB)

### 1.3 Security + Reliability Principles

- JWT stateless auth
- Role-based authorization (`customer`, `manager`)
- bcrypt password hashing
- Parameterized queries for SQL injection prevention
- Foreign keys + constraints for integrity
- Connection pooling for stable DB access

---

## 2. Database Design

### 2.1 Schema Summary (8 tables)

1. `users`
2. `books`
3. `orders`
4. `order_items`
5. `categories`
6. `book_categories`
7. `reviews`
8. `addresses`

### 2.2 Key Relationships

- `orders.customer_id -> users.id`
- `orders.address_id -> addresses.id` (`ON DELETE SET NULL`)
- `order_items.order_id -> orders.id`
- `order_items.book_id -> books.id`
- `addresses.user_id -> users.id`
- `book_categories.book_id -> books.id`
- `book_categories.category_id -> categories.id`
- `reviews.book_id -> books.id`
- `reviews.user_id -> users.id`

### 2.3 Normalization Notes

- Separate entity tables for users, books, categories, reviews, addresses, orders, and order items.
- Many-to-many genres solved through `book_categories` junction table.
- Duplicate-review prevention through unique `(book_id, user_id)` in `reviews`.
- Order shipping data normalized by referencing `addresses` instead of duplicating address fields per order.

### 2.4 Indexing

Important indexes:
- `books.isbn` unique index for exact ISBN lookup and deduplication
- `orders.customer_id` index for customer order history
- Existing indexes for search/filter fields (`title`, `author`, payment/date, FK columns)

Explicit index statements:

```sql
CREATE UNIQUE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

---

## 3. Backend API Design

### 3.1 Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`

JWT payload contains:
- `user_id`
- `username`
- `role`
- `exp`

Decorators:
- `login_required`: validates bearer token and attaches `request.user`
- `role_required('manager')`: enforces manager-only routes

### 3.2 Books + Catalog Endpoints

- `GET /api/books` (supports `q` search)
- `GET /api/books/<book_id>`
- `GET /api/books/categories`
- `GET /api/books/<book_id>/reviews`
- `POST /api/books/<book_id>/reviews` (customer review upsert)

### 3.3 Orders + Addresses Endpoints

- `POST /api/orders` (supports optional `address_id`)
- `GET /api/orders/<order_id>`
- `GET /api/orders/addresses`
- `POST /api/orders/addresses`

### 3.4 Manager Endpoints

- `GET /api/manager/orders`
- `GET /api/manager/orders/<order_id>`
- `PATCH /api/manager/orders/<order_id>/payment-status`
- `GET /api/manager/books`
- `POST /api/manager/books` (requires `isbn`)
- `PUT /api/manager/books/<book_id>` (requires `isbn`)
- `GET /api/manager/categories`
- `POST /api/manager/categories`

---

## 4. Database Access Layer

### 4.1 Connection Pooling (PyMySQL)

`backend/db.py` implements a custom pool using `Queue`:

- Pool class: `PyMySQLConnectionPool`
- Default size: `DB_POOL_SIZE=5`
- `get_connection()`:
  - pulls from queue
  - checks with `ping(reconnect=True)`
- `release_connection(conn)`:
  - returns to pool
  - recreates if closed

### 4.2 Query Execution Pattern

`execute_query(...)`:
1. get pooled connection
2. execute parameterized SQL
3. commit/rollback as needed
4. close cursor
5. release connection back to pool

This keeps DB access reusable and safe under concurrent requests.

---

## 5. Caching Strategy

### 5.1 LRU Cache for Book Search

`backend/cache.py` uses `OrderedDict`:

- Class: `BookSearchLRUCache`
- Max entries: 100
- Cache key: raw search query string `q`
- `get(query)`: moves key to recent end
- `set(query, value)`: inserts/updates and evicts least recently used when full
- `invalidate(query=None)`: clear one key or all

### 5.2 Invalidation Rules

Manager book writes call `cache.invalidate()`:
- `POST /api/manager/books`
- `PUT /api/manager/books/<book_id>`

This ensures cached search results never stay stale after catalog changes.

---

## 6. Security Implementation

### 6.1 Password Hashing

- Uses bcrypt with salt (`hashpw` / `checkpw`)
- Plaintext passwords are never stored

### 6.2 SQL Injection Prevention

- All DB operations use parameter placeholders (`%s`) + bound params
- No string-concatenated SQL for user input

### 6.3 Authorization Rules

- Customers can view/search books, place orders, manage own addresses, and review books
- Customers can only view their own orders
- Managers can manage books/categories and all orders

---

## 7. Performance Notes

- Indexed ISBN lookup avoids table scans for identifier search
- Indexed `orders.customer_id` accelerates order-history and joins
- LRU cache reduces repeated book search DB hits
- Connection pooling avoids connection setup overhead per request

---

## 8. Operational Setup

### 8.1 Environment Variables (`backend/.env`)

```env
SECRET_KEY=dev-secret-key-change-this
JWT_SECRET=another-secret-key-here
DEBUG=False
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=bookstore
DB_POOL_SIZE=5
CORS_ORIGINS=*
```

### 8.2 Run Commands

Backend:
```powershell
cd backend
python app.py
```

Desktop client:
```powershell
cd desktop_client
python main.py
```

---

## 9. Interview-Focused Talking Points

- “I evolved the schema from 4 to 8 normalized tables to model categories, reviews, and shipping addresses without denormalizing transactions.”
- “I introduced `isbn` uniqueness and indexed `customer_id` because they map to real high-frequency lookup patterns.”
- “I implemented a fixed-size PyMySQL connection pool (5) to reduce connection churn and improve request stability.”
- “I added an OrderedDict-based LRU cache for book searches, keyed by query string, with explicit invalidation on book writes.”
- “All SQL paths are parameterized and auth is JWT + role-based, so the API is secure and production-lean.”
