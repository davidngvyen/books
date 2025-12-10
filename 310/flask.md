# Lecture: Designing and Developing Web Services with RESTful APIs in Python Flask

## 1. Introduction: The Modern Web

Welcome! Today, we're diving into the backbone of modern web and mobile applications: web services and RESTful APIs.

### What is a Web Server?

At its core, a **web server** is a program that listens for incoming network requests (usually over HTTP) and sends back responses. When you type a URL into your browser, you're sending a request to a web server.

### What is a Web Service?

A **web service** is an application that runs on a web server and exposes a specific set of functionalities to other applications over the network. Instead of returning a full HTML page for a human to view, it typically returns raw data (like JSON) for another program to consume. This is the foundation of how your mobile app talks to its backend, or how different microservices in a large system communicate.

### What is a RESTful API?

**API** stands for **Application Programming Interface**. It's a set of rules and definitions that allows different software applications to communicate with each other.

**REST** (**RE**presentational **S**tate **T**ransfer) is an architectural style for designing these APIs. It's not a strict protocol but a set of guiding principles that make APIs simple, scalable, and easy to understand.

### Why Python and Flask?

*   **Python:** An incredibly popular, readable, and powerful language with a vast ecosystem of libraries.
*   **Flask:** A "micro" web framework for Python. It's lightweight, flexible, and unopinionated, making it a perfect choice for building everything from simple web services to complex applications. It provides the essentials without forcing you into a rigid structure.

---

## 2. Setting Up Your Environment

Before we write any code, let's get our tools ready.

### Prerequisites

*   Python 3.6+ installed.
*   `pip` (Python's package installer), which usually comes with Python.

### Step 1: Create a Project Directory

```bash
mkdir flask-api-project
cd flask-api-project
```

### Step 2: Create and Activate a Virtual Environment

Using a virtual environment is a crucial best practice. It isolates your project's dependencies from your global Python installation.

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

You'll know it's active because your command prompt will be prefixed with `(venv)`.

### Step 3: Install Flask

With your virtual environment active, install Flask using pip.

```bash
pip install Flask
```

That's it! Our environment is ready.

---

## 3. Flask Fundamentals: "Hello, World!"

Let's create the simplest possible Flask application to understand the core concepts.

Create a file named `app.py`:

```python
# app.py
from flask import Flask

# Create an instance of the Flask class
app = Flask(__name__)

# Define a "route" and the function to handle it
@app.route('/')
def hello_world():
    return 'Hello, World!'

# This block allows you to run the app directly
if __name__ == '__main__':
    # The debug=True flag enables a helpful debugger
    app.run(debug=True)
```

**To run your server:**

```bash
python app.py
```

You will see output like this:

```
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
```

Now, open your web browser and navigate to `http://127.0.0.1:5000/`. You should see the text "Hello, World!".

**Key Concepts:**

*   `app = Flask(__name__)`: This line creates the central Flask application object.
*   `@app.route('/')`: This is a **decorator**. It tells Flask that the function `hello_world()` should be triggered whenever a request comes in for the URL path `/`. This is called **routing**.

---

## 4. Designing a RESTful API

Before we code our API, we need to *design* it. Good design follows REST principles.

### Core Principles of REST

1.  **Resources:** The key abstraction in REST is a **resource**. A resource is any object or piece of information you want to expose, like a user, a product, or a to-do item. Resources are identified by **URIs** (Uniform Resource Identifiers), like `/users/123`. **Use nouns, not verbs.**
    *   Good: `/books/1`
    *   Bad: `/getBookById?id=1`

2.  **HTTP Methods (Verbs):** You use standard HTTP methods to operate on these resources. This maps directly to **CRUD** (Create, Read, Update, Delete) operations.

| HTTP Method | Action | CRUD Equivalent |
| :--- | :--- | :--- |
| `GET` | Retrieve a resource or a collection of resources. | **Read** |
| `POST` | Create a new resource. | **Create** |
| `PUT` | Update/replace an existing resource completely. | **Update** |
| `DELETE` | Delete a resource. | **Delete** |
| `PATCH` | Partially update an existing resource. | **Update** |

3.  **Representations:** The server doesn't send the resource itself (e.g., the object in memory). It sends a *representation* of the resource's state. The most common format for this is **JSON** (JavaScript Object Notation) because it's lightweight and easy for machines to parse.

4.  **Statelessness:** Every request from a client to the server must contain all the information needed for the server to fulfill that request. The server does not store any client "session" or "state" between requests.

### HTTP Status Codes

Your API should use standard HTTP status codes to inform the client about the outcome of its request.

*   **2xx (Success):**
    *   `200 OK`: The request was successful (used for `GET`, `PUT`).
    *   `201 Created`: A new resource was successfully created (used for `POST`).
    *   `204 No Content`: The request was successful, but there's no data to return (used for `DELETE`).
*   **4xx (Client Error):**
    *   `400 Bad Request`: The server cannot process the request due to a client error (e.g., malformed JSON).
    *   `404 Not Found`: The requested resource could not be found.
*   **5xx (Server Error):**
    *   `500 Internal Server Error`: Something went wrong on the server.

---

## 5. Building a Simple To-Do List API

Let's apply these principles to build a REST API for managing a list of tasks.

We'll use a simple Python list of dictionaries as our in-memory "database".

Update your `app.py` file:

```python
# app.py
from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory "database"
tasks = [
    {
        'id': 1,
        'title': 'Learn Python',
        'description': 'Study functions, classes, and modules in Python.',
        'done': False
    },
    {
        'id': 2,
        'title': 'Learn Flask',
        'description': 'Build a simple web API with Flask.',
        'done': False
    }
]

# --- Helper Function ---
def find_task(task_id):
    """Finds a task by its ID in our list."""
    for task in tasks:
        if task['id'] == task_id:
            return task
    return None

# --- API Endpoints ---

# GET /tasks -> Retrieve all tasks
@app.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

# GET /tasks/<id> -> Retrieve a single task
@app.route('/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = find_task(task_id)
    if task is None:
        # Return 404 Not Found if the task doesn't exist
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({'task': task})

# POST /tasks -> Create a new task
@app.route('/api/v1/tasks', methods=['POST'])
def create_task():
    # Check if the request has JSON data and a 'title' field
    if not request.json or not 'title' in request.json:
        return jsonify({'error': 'Bad Request: Missing title in request body'}), 400

    new_task = {
        'id': tasks[-1]['id'] + 1 if tasks else 1, # Simple ID generation
        'title': request.json['title'],
        'description': request.json.get('description', ""), # Optional field
        'done': False
    }
    tasks.append(new_task)
    # Return 201 Created status code and the new task
    return jsonify({'task': new_task}), 201

# PUT /tasks/<id> -> Update an existing task
@app.route('/api/v1/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = find_task(task_id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    if not request.json:
        return jsonify({'error': 'Bad Request: No data provided'}), 400

    # Update fields if they are in the request JSON
    task['title'] = request.json.get('title', task['title'])
    task['description'] = request.json.get('description', task['description'])
    task['done'] = request.json.get('done', task['done'])

    return jsonify({'task': task})

# DELETE /tasks/<id> -> Delete a task
@app.route('/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = find_task(task_id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    tasks.remove(task)
    # Return 204 No Content to indicate successful deletion
    return '', 204


if __name__ == '__main__':
    app.run(debug=True)
```

### How to Test Your API

You can't use a browser for `POST`, `PUT`, or `DELETE` requests easily. Use a dedicated API client like Postman, Insomnia, or the command-line tool `curl`.

**Example using `curl`:**

```bash
# Get all tasks
curl -i http://127.0.0.1:5000/api/v1/tasks

# Get task with ID 1
curl -i http://127.0.0.1:5000/api/v1/tasks/1

# Create a new task
curl -i -X POST -H "Content-Type: application/json" -d '{"title": "Test with curl"}' http://127.0.0.1:5000/api/v1/tasks

# Update task with ID 3 to be done
curl -i -X PUT -H "Content-Type: application/json" -d '{"done": true}' http://127.0.0.1:5000/api/v1/tasks/3

# Delete task with ID 3
curl -i -X DELETE http://127.0.0.1:5000/api/v1/tasks/3
```
The `-i` flag in `curl` shows the response headers, including the important status code.

---

## 6. Best Practices and Next Steps

Our API works, but here's how to make it production-ready.

### API Versioning

Notice our URL is `/api/v1/tasks`. This is a great practice. If you need to make breaking changes to your API in the future, you can introduce a `/api/v2/...` without breaking existing client applications.

### Authentication

Our API is open to everyone. In the real world, you'd need to secure it. Common methods include:
*   **API Keys:** A simple token passed in a request header.
*   **OAuth2:** A robust framework for delegated access (e.g., "Login with Google").
*   **JWT (JSON Web Tokens):** A popular method for creating access tokens that assert some number of claims.

### From In-Memory to a Real Database

Our `tasks` list is cleared every time the server restarts. The next logical step is to connect your Flask app to a real database like **PostgreSQL** or **MySQL**. The **SQLAlchemy** library is the de-facto standard for working with SQL databases in Python.

### Documentation

How will other developers know how to use your API? You need to document it. Tools like **Swagger/OpenAPI** allow you to create interactive API documentation that is easy to explore and test.

## Conclusion

You have successfully designed, built, and tested a RESTful API using Python and Flask! You've learned the fundamental principles of REST, the core mechanics of Flask, and the path forward to building robust, production-grade web services.