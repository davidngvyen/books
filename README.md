# Online Bookstore (Flask + MySQL + Desktop Client)

This project contains:
- `backend/` – Flask REST API
- `desktop_client/` – Python Tkinter desktop application
- `database/` – MySQL schema

Run backend first, then desktop client.

## 1) Prerequisites

- Python 3.10+
- MySQL Server 5.7+ / 8+
- `pip`

Install backend dependencies:

```powershell
cd backend
pip install flask flask-cors python-dotenv pymysql bcrypt pyjwt
```

Install desktop client dependencies:

```powershell
cd ../desktop_client
pip install requests
```

## 2) Database Setup

1. Start MySQL.
2. Create database (optional, schema also creates it):

```sql
CREATE DATABASE IF NOT EXISTS bookstore;
```

3. Run schema file:
- `database/schema.sql`

Schema now includes **8 normalized tables**:
- `users`
- `books` (with `isbn` unique)
- `orders` (with `customer_id`)
- `order_items`
- `categories`
- `book_categories`
- `reviews`
- `addresses`

## 3) Environment Configuration

Create `backend/.env`:

```env
SECRET_KEY=dev-secret-key-change-this
JWT_SECRET=another-secret-key-here
DEBUG=False

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=bookstore
DB_POOL_SIZE=5

CORS_ORIGINS=*
```

## 4) Run Backend

```powershell
cd backend
python app.py
```

Backend runs at `http://localhost:5000`.

## 5) Run Desktop Client

```powershell
cd ../desktop_client
python main.py
```

## 6) Implemented Highlights

- JWT authentication + role-based authorization (`customer`, `manager`)
- bcrypt password hashing
- Parameterized SQL queries (SQL injection prevention)
- PyMySQL connection pooling (`DB_POOL_SIZE`, default 5)
- LRU book-search cache (`OrderedDict`, key = query string, max 100)
- Cache invalidation on book create/update
- Review endpoints and category mapping support
- Address management + order shipping-address support

## 7) Core API Endpoints

- Auth: `/api/auth/register`, `/api/auth/login`
- Books: `/api/books`, `/api/books/categories`, `/api/books/<id>/reviews`
- Orders: `/api/orders`, `/api/orders/<id>`, `/api/orders/addresses`
- Manager: `/api/manager/orders`, `/api/manager/books`, `/api/manager/categories`

## 8) Notes

- Orders now reference `customer_id` (not `user_id`).
- `books.isbn` is unique and indexed.
- `orders.customer_id` is indexed for order history performance.
