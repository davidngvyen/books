# Database Examination Notes – Bookstore Schema (Updated)

## 1. Notes To Remember

- The schema now has **8 normalized tables**: `users`, `books`, `orders`, `order_items`, `categories`, `book_categories`, `reviews`, and `addresses`.
- Primary transaction flow is still `users -> orders -> order_items -> books`, but now orders can also reference `addresses` and books can be linked to many categories.
- Key foreign key relationships are:
  - `orders.customer_id` references `users.id`.
  - `orders.address_id` references `addresses.id`.
  - `order_items.order_id` references `orders.id`.
  - `order_items.book_id` references `books.id`.
  - `addresses.user_id` references `users.id`.
  - `book_categories.book_id` references `books.id`.
  - `book_categories.category_id` references `categories.id`.
  - `reviews.book_id` references `books.id`.
  - `reviews.user_id` references `users.id`.
- The `books` table now includes `isbn` and enforces uniqueness.
- The `orders` table now uses `customer_id` (instead of `user_id`) and has an index on `customer_id`.
- `book_categories` is a junction table that models many-to-many between books and categories.
- `reviews` stores one review per user per book via unique key `(book_id, user_id)`.
- `addresses` supports shipping address history and default address selection.
- Indexes support common lookups by login, ISBN, search fields, customer order history, joins, and status/date filtering.

---

## 2. Simple Explanation

Imagine eight linked spreadsheets instead of four.

### `users`
Stores customer/manager accounts.

### `books`
Stores books for sale/rent.

- Includes `isbn` (unique per book record).

### `categories`
Stores genre names like Fiction, Science, History.

### `book_categories`
Links books to categories.

- One book can belong to many categories.
- One category can contain many books.

### `reviews`
Stores customer ratings and optional review text.

- One user can review a specific book once (then update it).

### `addresses`
Stores customer shipping addresses.

- One user can have many addresses.
- Supports a default address.

### `orders`
Stores checkout orders.

- Uses `customer_id` to link the buyer.
- Optionally uses `address_id` for shipping destination.

### `order_items`
Stores each line item in an order.

- Each row is one `buy` or `rent` action for one book.

### Relationship chain

`users -> orders -> order_items -> books`

With extensions:

- `users -> addresses`
- `books <-> categories` through `book_categories`
- `users + books -> reviews`

---

## 3. Detailed Explanation

### 3.1 Tables, Keys, and Relationships

#### `users`
- PK: `id`
- Unique: `username`, `email`
- Candidate keys: `id`, `username`, `email`

#### `books`
- PK: `id`
- Added: `isbn VARCHAR(20) NOT NULL`
- Unique constraint/index on `isbn`

#### `categories`
- PK: `id`
- Unique: `name`

#### `book_categories`
- Composite PK: `(book_id, category_id)`
- Pure junction table for many-to-many modeling

#### `reviews`
- PK: `id`
- FK: `book_id`, `user_id`
- Unique key: `(book_id, user_id)` (prevents duplicate reviews by same user for same book)
- Check constraint: `rating` in range 1..5

#### `addresses`
- PK: `id`
- FK: `user_id`
- Includes address fields + `is_default`

#### `orders`
- PK: `id`
- FK: `customer_id -> users.id`
- FK: `address_id -> addresses.id` (nullable, `ON DELETE SET NULL`)
- Uses status + timestamp for operational reporting

#### `order_items`
- PK: `id`
- FK: `order_id`, `book_id`
- `item_type` in `buy` or `rent`

### 3.2 Normalization Summary

- **1NF**: No repeating groups; atomic columns.
- **2NF**: Non-key columns depend on whole primary key (especially in junction table).
- **3NF**: Non-key columns depend only on key, not other non-key columns.
- **BCNF**: Determinants are candidate keys (plus controlled constraints like unique keys).

This design separates entities cleanly:
- account data (`users`)
- catalog data (`books`, `categories`, `book_categories`)
- customer feedback (`reviews`)
- customer shipping profile (`addresses`)
- transactions (`orders`, `order_items`)

### 3.3 Indexes and Why They Matter

Important indexes now include:
- `books.isbn` (unique): fast exact ISBN lookup + uniqueness guarantee
- `orders.customer_id`: fast “show all orders for this customer” queries
- Existing operational indexes on payment status/date, join columns, and search columns

**Explicit statements used in schema:**

```sql
CREATE UNIQUE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

### 3.4 Common Exam-Style Query Examples

**Find all orders for a specific customer (new column name):**

```sql
SELECT *
FROM orders
WHERE customer_id = ?
ORDER BY created_at DESC;
```

**Find a book by ISBN:**

```sql
SELECT *
FROM books
WHERE isbn = ?;
```

**List categories for a given book:**

```sql
SELECT c.id, c.name
FROM categories c
JOIN book_categories bc ON bc.category_id = c.id
WHERE bc.book_id = ?
ORDER BY c.name;
```

**List reviews for a book:**

```sql
SELECT r.rating, r.review_text, r.created_at, u.username
FROM reviews r
JOIN users u ON u.id = r.user_id
WHERE r.book_id = ?
ORDER BY r.created_at DESC;
```

**Use customer default address in checkout flow (conceptual):**

```sql
SELECT *
FROM addresses
WHERE user_id = ? AND is_default = TRUE
LIMIT 1;
```

---

## 4. Updated Exam Q&A

**Q1: Why add `categories` + `book_categories` instead of a single category column in `books`?**

**A:** Because one book can belong to multiple genres, and one genre can include many books. This is a many-to-many relationship, so a junction table is the normalized design.

---

**Q2: Why add `isbn` with a unique index?**

**A:** ISBN is a real-world identifier used for exact lookup and deduplication. Uniqueness prevents duplicate catalog records for the same ISBN and improves performance for ISBN-based searches.

---

**Q3: Why rename `orders.user_id` to `orders.customer_id`?**

**A:** It improves domain clarity in a marketplace context and makes interview discussion clearer: the order is placed by a customer account.

---

**Q4: How does the schema prevent duplicate reviews by the same user for the same book?**

**A:** The unique key `(book_id, user_id)` in `reviews` enforces one review row per user-book pair.

---

**Q5: What is the benefit of indexing `orders.customer_id`?**

**A:** It speeds up customer order-history queries and improves join/filter performance on a very common access pattern.

---

**Q6: Does this design track physical inventory copies?**

**A:** No. It tracks catalog-level books and transaction events. To track physical copies, add a separate inventory/copies table.

---

**Q7: What kind of normalization issues were solved by adding `addresses`?**

**A:** Address data is no longer duplicated across orders. A user can store multiple addresses and orders can reference one address row.

---

**Q8: How do B+ tree indexes help here?**

**A:** They reduce disk/page reads for equality and range lookups (e.g., ISBN lookup, customer order history, date/status filters), which is critical as row counts grow.

---

## 5. Interview-Ready Summary (30-second version)

- I designed an **8-table normalized MySQL schema** for a bookstore.
- I modeled **many-to-many book genres** with `categories` and `book_categories`.
- I added **reviews** with a uniqueness rule to enforce one review per customer per book.
- I added **customer addresses** and linked orders to selected shipping addresses.
- I added **ISBN uniqueness** and indexed **`orders.customer_id`** to optimize real query patterns.
- The design is cleanly normalized, enforces referential integrity, and scales with indexed access paths.
