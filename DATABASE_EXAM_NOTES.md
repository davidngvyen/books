# Database Examination Notes – Bookstore Schema

## 1. Notes To Remember

- The tables `users`, `books`, `orders`, and `order_items` form a classic relational bookstore schema.
- The columns `id` in each table are surrogate primary keys generated automatically.
- Foreign key relationships are:
  - `orders.user_id` references `users.id`.
  - `order_items.order_id` references `orders.id`.
  - `order_items.book_id` references `books.id`.
- One user can have many orders, one order can have many order items, and one book can appear in many order items.
- All four tables are in First Normal Form, Second Normal Form, Third Normal Form, and they also satisfy Boyce–Codd Normal Form, because all non key attributes depend directly on the key and there are no transitive dependencies.
- There is no separate table for physical copies of a book, so the database records transactions for books, but it does not track individual physical copies.
- Indexes on username, email, role, title, author, available flag, user identifier, payment status, creation time, order identifier, book identifier, and item type help the database search and join quickly.
- MySQL uses B plus tree indexes for these normal secondary indexes, which are good for equality searches and range scans.
- Each row in `order_items` represents one purchase or rental of a book at a particular time.
- Deleting a user or a book automatically deletes related orders and order items because of the “on delete cascade” rule on the foreign keys.

---

## 2. Simple Explanation

Imagine four spreadsheets that are linked together by identifier columns.

### The `users` Table

This table stores the people who use the bookstore system.

- Each row is one person.
- Important columns:
  - `id`: a unique identifier number for each user.
  - `username`: a unique login name.
  - `email`: a unique email address.
  - `password_hash`: an encrypted version of the user password.
  - `role`: either `customer` or `manager`.
  - `created_at`: the time when the user account was created.

### The `books` Table

This table stores information about the books.

- Each row is one logical book (for example, a specific title and author), not a particular physical copy.
- Important columns:
  - `id`: unique identifier for the book.
  - `title`: the title of the book.
  - `author`: the author of the book.
  - `price_buy`: how much it costs to buy the book.
  - `price_rent`: how much it costs to rent the book.
  - `available`: a flag that says whether the book is available.
  - `created_at` and `updated_at`: times when the row was created and last updated.

### The `orders` Table

This table stores orders placed by users.

- Each row is one order.
- Important columns:
  - `id`: unique identifier for the order.
  - `user_id`: which user placed the order, pointing to the `users` table.
  - `total_amount`: total amount of money for this order.
  - `payment_status`: whether the order is `Pending`, `Paid`, or `Cancelled`.
  - `created_at`: when the order was created.

### The `order_items` Table

This table stores the individual lines inside an order.

- Each row is one book in one order.
- Important columns:
  - `id`: unique identifier for the line item.
  - `order_id`: which order this line belongs to, pointing to `orders.id`.
  - `book_id`: which book this line refers to, pointing to `books.id`.
  - `item_type`: whether the line is a `buy` or `rent` action.
  - `price`: the price charged for this line.
  - `created_at`: when this line was created.

### How the Tables Connect

- One user can have many orders.
- One order can have many order items.
- One book can appear in many order items.

In a chain, it looks like this:

`users` → `orders` → `order_items` → `books`

### Multiple Rentals Over Time

Every time a user buys or rents a book, the system inserts a row into `order_items`. That means the same book can appear in many order items at different times. This captures the history of purchases and rentals. However, because there is no table for physical copies, the system does not know how many copies exist or which specific copy is rented at any moment.

### Normalization In Simple Terms

- Each table describes a single type of entity: user, book, order, or order item.
- There are no repeating columns like `book1`, `book2`, and so on.
- Information about users is stored once in the `users` table, and referenced by identifier in other tables. The same is true for books.
This is what a well normalized relational design looks like.

---

## 3. Detailed Explanation

### 3.1 Tables, Keys, and Relationships

#### The `users` Table

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer', 'manager') NOT NULL DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);
```

- The primary key is `id`.
- The columns `username` and `email` are also candidates to uniquely identify a user, because they are marked as unique.
- Functional dependencies in this table include:
  - `id` determines all the other columns.
  - Because `username` is unique, `username` also determines all other columns.
  - Because `email` is unique, `email` also determines all other columns.
- Normal forms:
  - First Normal Form: all attributes are atomic, there are no repeating groups.
  - Second Normal Form: the primary key uses a single column, so there is no partial dependency.
  - Third Normal Form: there is no non key attribute that depends on another non key attribute, so there are no transitive dependencies.
  - Boyce–Codd Normal Form: whenever one set of columns determines another, the determining set is a key. Here, the determining sets are `id`, `username`, and `email`, and all of them are keys.

The indexes on `username`, `email`, and `role` allow MySQL to search by these columns very quickly by using B plus tree index structures.

#### The `books` Table

```sql
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    price_buy DECIMAL(10, 2) NOT NULL,
    price_rent DECIMAL(10, 2) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_available (available)
);
```

- The primary key is `id`.
- There is no constraint that forces title and author to be unique, so two rows can have the same title and author if needed.
- The functional dependency is that `id` determines all other columns in the row.
- Normal forms:
  - First Normal Form: each column holds a single value.
  - Second Normal Form: the key is one column, so there cannot be a partial dependency.
  - Third Normal Form and Boyce–Codd Normal Form: there are no additional dependencies between non key attributes, so these forms are satisfied.

The indexes on title, author, and availability support searches such as “find all books by this author” or “find all books that are currently available”.

#### The `orders` Table

```sql
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('Pending', 'Paid', 'Cancelled') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_payment_status (payment_status),
    INDEX idx_created_at (created_at)
);
```

- The primary key is `id`.
- The foreign key `user_id` references `users.id` and has an “on delete cascade” rule. That means when a user is deleted, all of that user’s orders are also deleted automatically.
- The functional dependency is that `id` determines `user_id`, `total_amount`, `payment_status`, and `created_at`.
- Normal forms are satisfied for the same reasons as the earlier tables.

Indexes on `user_id`, `payment_status`, and `created_at` help with common queries such as “all orders by a user”, “all pending orders”, or “orders in a date range”.

#### The `order_items` Table

```sql
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    item_type ENUM('buy', 'rent') NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_book_id (book_id),
    INDEX idx_item_type (item_type)
);
```

- The primary key is `id`.
- The foreign key `order_id` references `orders.id`, and the foreign key `book_id` references `books.id`. Both have “on delete cascade”, so related line items are removed automatically when an order or a book is deleted.
- The functional dependency is that `id` determines `order_id`, `book_id`, `item_type`, `price`, and `created_at`.
- Normal forms are again satisfied up to Boyce–Codd Normal Form.

Indexes on `order_id`, `book_id`, and `item_type` are important for joins and for analysis such as “all items in this order”, “all rentals of this book”, or “how many items were rentals versus purchases”.

### 3.2 Modeling Multiple Rentals Over Time

Every row in `order_items` is one event: a specific user at a specific time bought or rented a particular book. To see all the times a book was rented or bought, you can join `order_items` with `orders` and filter by `book_id`.

```sql
SELECT oi.*, o.user_id, o.created_at
FROM order_items AS oi
JOIN orders AS o ON oi.order_id = o.id
WHERE oi.book_id = ?;
```

This query lists every transaction involving that book. However, because there is no separate table for physical copies of books, this design does not limit how many simultaneous rentals can occur, and it does not record which exact copy of a book a user has.

### 3.3 MySQL Internals And Indexes

MySQL with the InnoDB storage engine stores data in fixed size pages on disk. Each page holds many rows. When the database answers a query, it loads pages into memory through the buffer pool. Minimizing the number of page reads is critical for performance.

To help with this, MySQL builds indexes using B plus tree structures. A B plus tree has many keys in each internal node, which gives a high branching factor. This keeps the tree shallow, usually only a few levels deep, even for millions of rows. To find a row by an indexed column, MySQL walks from the root of the tree through the internal nodes down to a leaf node and then follows a pointer to the actual table row. This process is very efficient in terms of disk input and output.

Binary search trees would be inefficient on disk because they store fewer keys per node, which makes the tree tall and increases the number of disk reads. B plus trees are therefore preferred in database management systems.

### 3.4 Scalability Considerations

With one million books and ten thousand users, plus many orders and order items, the schema itself remains valid. Performance will depend on the specific queries. Queries that use indexed columns in their conditions can often be answered by scanning only a small portion of the index and data pages.

However, queries such as `SELECT * FROM books WHERE title LIKE '%Harry%'` are problematic because the leading percentage sign prevents use of the B plus tree index. MySQL then has to scan many rows. To handle this at large scale, you would consider full text search indexes or different query patterns that can use index prefixes.

---

## 4. Exam Style Questions And Answers

**Question 1:** In the `users` table, what is the primary key and what other columns can uniquely identify a user?

**Answer 1:** The primary key is the `id` column. The `username` column and the `email` column also uniquely identify a user because they are marked as unique.

---

**Question 2:** Describe the relationship between the `orders` table and the `users` table and explain how the schema enforces this relationship.

**Answer 2:** Each user can have many orders, so it is a one to many relationship. The `orders` table has a `user_id` column that references the `id` column in the `users` table through a foreign key constraint with an “on delete cascade” rule. This ensures that every order belongs to an existing user and that deleting a user automatically deletes that user’s orders.

---

**Question 3:** Are the tables `users`, `books`, `orders`, and `order_items` in Third Normal Form? Explain why.

**Answer 3:** Yes, they are in Third Normal Form. In each table the primary key consists of a single column `id`. All other columns depend directly on that primary key. There are no attributes that depend on only part of a key, and there are no attributes that depend on another non key attribute. Therefore, Second Normal Form and Third Normal Form are both satisfied.

---

**Question 4:** Does this schema model multiple physical copies of a book that can be rented at different times? Why or why not?

**Answer 4:** The schema models multiple rentals of a book over time but does not model physical copies. The `order_items` table records each rental or purchase event for a book, so it captures the history of use. However, there is no separate table for physical copies with a copy identifier and status, so the system does not know how many copies exist or which copy is rented.

---

**Question 5:** Consider the query:

```sql
SELECT *
FROM orders
WHERE user_id = ?
ORDER BY created_at DESC;
```

Which indexes in your schema are useful for this query, and how will MySQL use them?

**Answer 5:** The index on `user_id` in the `orders` table is useful. MySQL can use this B plus tree index to find all orders that belong to the given user by scanning only the relevant part of the index. After that, it will sort the resulting rows by `created_at`. If there were also a combined index on (`user_id`, `created_at`), MySQL could even return the rows already ordered without a separate sort step.

---

**Question 6:** Why does MySQL use B plus trees instead of simple binary search trees for indexes such as the index on `title` in the `books` table?

**Answer 6:** MySQL uses B plus trees because they are optimized for disk based storage. Each node in a B plus tree can hold many keys, which reduces the height of the tree and the number of disk pages that must be read to locate a key. Binary search trees have a smaller branching factor, which leads to taller trees and more input and output operations on disk. B plus trees also support efficient range queries, which are common in database workloads.

---

**Question 7:** What happens to rows in the `order_items` table when a row in the `books` table is deleted?

**Answer 7:** The foreign key on `order_items.book_id` references `books.id` with an “on delete cascade” rule. When a book row is deleted, MySQL automatically deletes all rows in `order_items` that reference that book, which preserves referential integrity and prevents orphaned order item rows.

---

**Question 8:** Write a query that computes the total revenue from all orders with payment status `Paid` during the last seven days, and mention which indexes help this query.

**Answer 8:**

```sql
SELECT SUM(total_amount) AS total_revenue
FROM orders
WHERE created_at >= NOW() - INTERVAL 7 DAY
  AND payment_status = 'Paid';
```

The index on `created_at` can help filter rows by date range, and the index on `payment_status` can help filter by payment status. The query optimizer will consider these indexes when choosing an execution plan.

---

**Question 9:** With one million rows in the `books` table, explain why the query `SELECT * FROM books WHERE title LIKE '%Harry%'` can be slow, and suggest an improvement.

**Answer 9:** The leading percentage symbol in the pattern prevents MySQL from using the B plus tree index on the `title` column, because the index is organized by prefix order. As a result, MySQL may need to scan many rows in the table, which is slow for one million rows. One improvement is to change the pattern to `title LIKE 'Harry%'`, which allows the index to be used. Another improvement is to use a full text index and the `MATCH ... AGAINST` syntax for more advanced text searching.

---

**Question 10:** Is this schema more suited for a relational database system or a NoSQL database system? Explain in the context of your design.

**Answer 10:** This schema is clearly suited for a relational database system. Data is divided into normalized tables with primary keys and foreign keys that model relationships. The design makes strong use of joins and enforces referential integrity. A NoSQL design would more likely store orders and their items as nested documents rather than separating them into normalized tables.
