### Lecture: Using SQLAlchemy with Python

#### Introduction

Welcome! This lecture will guide you through SQLAlchemy, a powerful SQL toolkit and Object-Relational Mapper (ORM) for Python. SQLAlchemy provides a full suite of well-known enterprise-level persistence patterns, designed for efficient and high-performing database access.

We'll explore how SQLAlchemy simplifies database interactions, moving from raw SQL strings to Python objects, which makes your code more robust, secure, and maintainable.

#### What is an ORM?

An Object-Relational Mapper (ORM) is a library that automates the transfer of data between a relational database (like MySQL, PostgreSQL) and an object-oriented programming language (like Python).

Instead of writing SQL queries like:
`INSERT INTO employees (name, salary) VALUES ('John Doe', 50000);`

You work with Python objects:
`new_employee = Employee(name='John Doe', salary=50000)`
`session.add(new_employee)`

**Benefits of using an ORM like SQLAlchemy:**
*   **Abstraction:** You can think in terms of Python objects instead of database tables and schemas.
*   **Security:** Automatically provides protection against SQL injection attacks.
*   **Portability:** It's easier to switch between different database systems (e.g., from SQLite to PostgreSQL) with minimal code changes.
*   **Productivity:** Reduces the amount of boilerplate code you need to write for CRUD (Create, Read, Update, Delete) operations.

#### Prerequisites

*   Python 3.6+
*   `pip` package installer
*   A database server installed (e.g., MySQL, PostgreSQL, SQLite).

#### 1. Installation

First, you need to install SQLAlchemy. You also need to install a "DBAPI driver" for the specific database you want to connect to.

```bash
# Install SQLAlchemy
pip install SQLAlchemy

# Install a driver for your database (choose one)
# For MySQL
pip install mysql-connector-python
# For PostgreSQL
pip install psycopg2-binary
```
For this lecture, we will use MySQL as an example.

#### 2. The SQLAlchemy Engine and Session

The **Engine** is the starting point for any SQLAlchemy application. It's a global object that manages connections to the database.

A **Session** is your primary interface for persisting objects to the database. Think of it as a temporary "workspace" for all the objects you have loaded or associated with it.

Here's how you set up the Engine and Session:

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection string
# Format: 'dialect+driver://username:password@host:port/database'
db_url = 'mysql+mysqlconnector://root:pass@localhost/cs310'

# Create an engine
engine = create_engine(db_url, echo=True) # echo=True logs all generated SQL

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a Session
session = Session()

try:
    # Use the session to execute a raw SQL query (for testing connection)
    connection = engine.connect()
    result = connection.execute(text("SELECT 'hello world'"))
    print(result.all())
    print("Connection to the database was successful!")
except Exception as e:
    print("Error connecting to the database:", e)
finally:
    # Close the session
    session.close()
    # The engine's connection is typically managed automatically
```

#### 3. Defining Models (Declarative Base)

In SQLAlchemy, you define your database tables as Python classes. These classes inherit from a `DeclarativeBase`.

```python
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker

# Define a base class for our models
Base = declarative_base()

# Define the Employee model, which corresponds to an 'employees' table
class Employee(Base):
    __tablename__ = 'employees'

    employee_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    salary = Column(DECIMAL(10, 2))

    def __repr__(self):
        return f"<Employee(name='{self.name}', salary={self.salary})>"

# --- Setup from previous step ---
db_url = 'mysql+mysqlconnector://root:pass@localhost/cs310'
engine = create_engine(db_url)

# Create the table in the database if it doesn't exist
# This is equivalent to "CREATE TABLE IF NOT EXISTS ..."
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
```
**Explanation:**
*   `Base = declarative_base()`: Creates a base class that our ORM models will inherit from.
*   `class Employee(Base)`: Defines our model.
*   `__tablename__ = 'employees'`: Links the class to the `employees` database table.
*   `Column(...)`: Defines a column in the table, specifying its data type and constraints (`primary_key`, `nullable`).

#### 4. CRUD Operations with the ORM

Now let's perform CRUD operations using our `Employee` model and the `session`.

```python
# Assume engine and session are already created as above

# --- CREATE (Insert) ---
print("\n--- Inserting new employees ---")
new_employee_1 = Employee(name="Alice", salary=75000.00)
new_employee_2 = Employee(name="Bob", salary=80000.00)

session.add(new_employee_1)
session.add(new_employee_2)
# You can also add multiple objects at once
# session.add_all([new_employee_1, new_employee_2])

session.commit() # This saves the changes to the database
print("New employees inserted.")

# --- READ (Select) ---
print("\n--- Querying all employees ---")
all_employees = session.query(Employee).all()
for emp in all_employees:
    print(emp)

print("\n--- Querying a specific employee ---")
alice = session.query(Employee).filter_by(name="Alice").first()
print(f"Found: {alice}")

# --- UPDATE ---
print("\n--- Updating an employee's salary ---")
employee_to_update = session.query(Employee).filter_by(name="Alice").first()
if employee_to_update:
    employee_to_update.salary = 78000.00
    session.commit()
    print("Employee updated.")

# Verify the update
updated_alice = session.query(Employee).filter_by(name="Alice").first()
print(f"After update: {updated_alice}")

# --- DELETE ---
print("\n--- Deleting an employee ---")
employee_to_delete = session.query(Employee).filter_by(name="Bob").first()
if employee_to_delete:
    session.delete(employee_to_delete)
    session.commit()
    print("Employee deleted.")

# Verify deletion
bob = session.query(Employee).filter_by(name="Bob").first()
print(f"Searching for Bob after deletion: {bob}") # Should be None

# Close the session when you're done
session.close()
```

#### 5. Best Practices

*   **Use Sessions for Queries:** The `session` object is the gateway to the database for all ORM operations.
*   **Context Managers for Sessions:** To ensure sessions are always closed, even if errors occur, use a `with` statement.

    ```python
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as session:
            # Create
            session.add(Employee(name="Charlie", salary=90000))
            session.commit() # commit flushes changes and makes them permanent
    
            # Read
            charlie = session.query(Employee).filter_by(name="Charlie").first()
            print(charlie)
    except Exception as e:
        print(f"An error occurred: {e}")
        # The 'with' block ensures session.close() is called,
        # and if an error happened before commit, changes are rolled back.
    ```
*   **Separate Model Definitions:** In a real application, you would place your model classes (`Employee`) in a separate file (e.g., `models.py`) to keep your code organized.

#### Conclusion

SQLAlchemy offers a powerful and Pythonic way to interact with relational databases. By mapping database tables to Python classes, it allows you to work with your data as objects, leading to cleaner, more readable, and more maintainable code. While there's a slight learning curve compared to raw SQL, the long-term benefits in productivity and code quality are substantial.

This lecture covered the basics of setting up SQLAlchemy, defining models, and performing CRUD operations. From here, you can explore more advanced topics like relationships (one-to-one, one-to-many, many-to-many), complex queries, and migrations.