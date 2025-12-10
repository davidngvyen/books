# Lecture: Designing and Developing RESTful Web Services with Python, Flask, and MySQL

## 1. Introduction to Web Services and RESTful APIs

### What is a Web Server?
A **web server** is software and hardware that uses HTTP (Hypertext Transfer Protocol) and other protocols to respond to client requests made over the World Wide Web. Its main job is to display website content through storing, processing, and delivering web pages to users.

Examples: Apache, Nginx, and the development server built into Flask.

### What is a Web Service?
A **web service** is a standardized way for applications to communicate with each other over a network. Instead of serving human-readable web pages, it serves machine-readable data, typically in formats like JSON or XML. This allows different systems, written in different languages, to interoperate.

### What is an API?
An **API (Application Programming Interface)** is a set of rules and definitions that allows different software applications to communicate with each other. A web service exposes an API that clients can use.

### What is a RESTful API?
**REST (Representational State Transfer)** is an architectural style for designing networked applications. It's not a standard but a set of constraints. An API that adheres to these constraints is called **RESTful**.

**Key Principles of REST:**
1.  **Client-Server Architecture**: Separate the user interface concerns (client) from the data storage concerns (server).
2.  **Statelessness**: Each request from a client to a server must contain all the information needed to understand and complete the request. The server does not store any client context between requests.
3.  **Uniform Interface**: This is the fundamental principle of REST and simplifies the architecture. It has four guiding constraints:
    *   **Resource-Based**: URIs (e.g., `/api/v1/tasks`) are used to identify resources.
    *   **Manipulation of Resources Through Representations**: The client has a representation of a resource (like a JSON object) and can use it to modify or delete the resource on the server.
    *   **Self-descriptive Messages**: Each request contains enough information for the server to process it (e.g., `Content-Type: application/json`).
    *   **Hypermedia as the Engine of Application State (HATEOAS)**: Responses can include links to other related actions (e.g., a response for a task might include a link to delete it).

## 2. Our Toolkit: Python, Flask, and MySQL

*   **Python**: A versatile, high-level programming language known for its readability and extensive libraries.
*   **Flask**: A "micro" web framework for Python. It's lightweight and flexible, making it perfect for building APIs without imposing a rigid structure.
*   **MySQL**: A popular, open-source relational database management system (RDBMS). It will be our persistent data store, ensuring our data survives even if the server restarts.
*   **`mysql-connector-python`**: The official Oracle driver for connecting Python applications to MySQL.

## 3. Setting Up the Development Environment

First, ensure you have Python and MySQL Server installed. Then, set up a virtual environment and install the necessary Python packages.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install Flask and the MySQL connector
pip install Flask mysql-connector-python
```

## 4. Designing Our "To-Do List" API

Before writing code, we must design the API. We'll manage a collection of "tasks".

**Resource**: Task
**Data Model**: A task will have an `id`, `title`, `description`, and a `done` status.

```json
{
    "id": 1,
    "title": "Learn REST APIs",
    "description": "Study the principles of REST.",
    "done": false
}
```

### API Endpoints (The "Uniform Interface")

We map CRUD (Create, Read, Update, Delete) operations to HTTP methods and URLs.

| **Operation** | **HTTP Method** | **URL** | **Action** |
| :--- | :--- | :--- | :--- |
| Read All | `GET` | `/api/v1/tasks` | Retrieve a list of all tasks. |
| Read One | `GET` | `/api/v1/tasks/<id>` | Retrieve a single task by its ID. |
| Create | `POST` | `/api/v1/tasks` | Create a new task. |
| Update | `PUT` | `/api/v1/tasks/<id>` | Update an existing task. |
| Delete | `DELETE` | `/api/v1/tasks/<id>` | Delete a task. |

## 5. Database Schema (MySQL)

Let's create a database and a table to store our tasks. Connect to your MySQL server and run the following SQL commands.

```sql
-- Create a new database for our application
CREATE DATABASE IF NOT EXISTS flask_api_db;

-- Switch to the new database
USE flask_api_db;

-- Create the 'tasks' table
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    done BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- (Optional) Insert some sample data to get started
INSERT INTO tasks (title, description) VALUES
('Learn Python', 'Study functions, classes, and modules in Python.'),
('Learn Flask', 'Build a simple web API with Flask.'),
('Do course project', 'Build web services with Flask and client app in Python.');
```

## 6. Building the Flask API with MySQL Integration

Now we'll modify our Flask application to connect to our new MySQL database instead of using an in-memory list. This makes our data persistent.

### Key Changes:
1.  **Database Configuration**: Store database credentials.
2.  **Connection Handling**: Create functions to connect to and close the database connection. Using a dictionary cursor (`dictionary=True`) is crucial for easily converting database rows to JSON.
3.  **Refactor Endpoints**: Replace list manipulations (`find_task`, `tasks.append`, `tasks.remove`) with SQL queries.

Here is the updated code.

```python
# app.py
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# --- Database Configuration ---
db_config = {
    'host': 'localhost',
    'database': 'flask_api_db',
    'user': 'your_mysql_user',      # <-- IMPORTANT: Change to your MySQL username
    'password': 'your_mysql_password' # <-- IMPORTANT: Change to your MySQL password
}

# --- Helper Function to get DB connection ---
def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# --- API Endpoints ---

# GET /tasks -> Retrieve all tasks
@app.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True) # dictionary=True returns rows as dicts
    cursor.execute("SELECT id, title, description, done FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'tasks': tasks})

# GET /tasks/<id> -> Retrieve a single task
@app.route('/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, description, done FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    cursor.close()
    conn.close()

    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({'task': task})

# POST /tasks -> Create a new task
@app.route('/api/v1/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        return jsonify({'error': 'Bad Request: Missing title in request body'}), 400

    new_task_data = {
        'title': request.json['title'],
        'description': request.json.get('description', "")
    }

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    query = "INSERT INTO tasks (title, description) VALUES (%s, %s)"
    cursor.execute(query, (new_task_data['title'], new_task_data['description']))
    new_id = cursor.lastrowid
    conn.commit() # Commit the transaction to save the change
    cursor.close()
    conn.close()

    # Fetch the newly created task to return it
    new_task = {'id': new_id, 'done': False, **new_task_data}
    return jsonify({'task': new_task}), 201

# PUT /tasks/<id> -> Update an existing task
@app.route('/api/v1/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if not request.json:
        return jsonify({'error': 'Bad Request: No data provided'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    # First, check if the task exists
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    if task is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    # Update fields if they are in the request JSON
    update_data = {
        'title': request.json.get('title', task['title']),
        'description': request.json.get('description', task['description']),
        'done': request.json.get('done', task['done'])
    }

    query = "UPDATE tasks SET title = %s, description = %s, done = %s WHERE id = %s"
    cursor.execute(query, (update_data['title'], update_data['description'], update_data['done'], task_id))
    conn.commit()

    # Fetch the updated task to return it
    cursor.execute("SELECT id, title, description, done FROM tasks WHERE id = %s", (task_id,))
    updated_task = cursor.fetchone()
    cursor.close()
    conn.close()

    return jsonify({'task': updated_task})

# DELETE /tasks/<id> -> Delete a task
@app.route('/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = getdb_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    # Check if the task exists before deleting
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    # If it exists, delete it
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return '', 204 # 204 No Content is standard for successful deletion

if __name__ == '__main__':
    app.run(debug=True)
```

## 7. Conclusion and Next Steps

You have successfully designed and built a RESTful API with Flask that uses a persistent MySQL database.

**Key Takeaways:**
- **Design First**: A well-designed API is easier to build, test, and use.
- **Statelessness is Key**: Notice how our Flask app doesn't store any information about the client. Every request is self-contained.
- **Use Correct HTTP Methods and Status Codes**: This makes your API predictable and easy for clients to work with. (e.g., `GET` for fetching, `POST` for creating, `201 Created`, `404 Not Found`).
- **Separate Concerns**: The Flask app handles HTTP logic, and the database handles data storage.
- **Security**: Always use parameterized queries (e.g., `cursor.execute(query, params)`) to prevent SQL injection attacks.

**Further Improvements:**
- **Connection Pooling**: Opening a new database connection for every request is inefficient. For production, use a connection pool.
- **Configuration Management**: Move database credentials and other settings out of the code and into environment variables or a configuration file.
- **Error Handling**: Implement a more robust, centralized error handling mechanism.
- **Authentication & Authorization**: Secure your API so that only authorized users can access or modify data.
- **Testing**: Write automated tests for your API endpoints.

This foundation will allow you to build more complex and robust web services.