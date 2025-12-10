# Lecture: Introduction to Redis with Python

## 1. What is Redis?

**Redis** (which stands for **RE**mote **DI**ctionary **S**erver) is an open-source, in-memory data structure store. It's often referred to as a "data structure server" because its core data types are similar to those found in most programming languages, like strings, lists, hashes (dictionaries), sets, and sorted sets.

### Key Characteristics:

*   **In-Memory:** Redis primarily stores data in the server's main memory (RAM). This is what makes it incredibly fast for both read and write operations.
*   **Key-Value Store:** At its simplest, Redis is a key-value store. You store a piece of data (a "value") and assign it a unique "key". You then use that key to retrieve the value.
*   **Rich Data Types:** Unlike simple key-value stores that only handle strings, Redis values can be complex data structures. This is its superpower.
*   **Persistence:** Although it's in-memory, Redis can persist data to disk. This means your data can survive server restarts.
*   **Versatility:** It can be used as a database, a cache, and a message broker.

## 2. Why Use Redis? Common Use Cases

Redis's speed and data structures make it a perfect solution for a variety of problems:

*   **Caching:** This is the most common use case. You can store the results of expensive database queries or API calls in Redis. Subsequent requests for the same data can be served instantly from the Redis cache, dramatically reducing latency and database load.
*   **Session Store:** Storing user session data (e.g., login information, shopping cart contents) for a web application. It's much faster than reading and writing this data to a traditional database on every request.
*   **Real-time Analytics:** Use Redis to rapidly ingest and process large streams of data, like tracking user clicks on a website in real-time.
*   **Leaderboards & Rankings:** Redis's **Sorted Sets** are perfect for maintaining ordered lists, like a leaderboard in a gaming application. Adding new scores and retrieving the top N players is extremely efficient.
*   **Queues:** Redis **Lists** can be used to implement a simple, reliable message queue for background job processing. For example, when a user requests a report that takes time to generate, you can push a "job" onto a Redis list. A separate worker process can then pull jobs from that list and process them.
*   **Pub/Sub (Publish/Subscribe):** Redis provides commands for implementing a high-speed messaging system where "publishers" can send messages to channels, and "subscribers" can listen to those channels to receive messages in real-time.

## 3. Connecting to Redis with Python

To interact with Redis from Python, we use a client library. The most popular one is `redis-py`.

### Installation

First, install the library using pip:

```bash
pip install redis
```

### Establishing a Connection

You create a `Redis` client object, pointing it to your Redis server.

*   `host`: The server address (e.g., `localhost` for a local instance, or a cloud URL).
*   `port`: The port Redis is running on (default is `6379`).
*   `db`: Redis can have multiple databases, numbered 0-15. The default is 0.
*   `decode_responses=True`: This is a very useful setting. It decodes responses from Redis (which are bytes) into Python strings (UTF-8), saving you from doing `response.decode('utf-8')` on every result.

```python
# basic_connection.py
import redis

# --- Connect to a LOCAL Redis instance ---
# Assumes Redis is running on your machine at the default port.
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# --- Or, connect to a CLOUD Redis instance ---
# Example credentials for a cloud provider.
# r = redis.Redis(
#     host='your-cloud-redis-host.com',
#     port=10391,
#     username="default",
#     password="your-secure-password",
#     decode_responses=True,
# )

# Check if the connection is successful by sending a PING command.
# Redis will reply with PONG if it's alive.
try:
    is_connected = r.ping()
    print(f"Successfully connected to Redis: {is_connected}")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")

```

## 4. Redis Data Types in Python

Let's explore the main data types and how to use them with `redis-py`.

### Strings

The simplest data type. One key holds one string value.

```python
# strings_example.py
import redis

r = redis.Redis(decode_responses=True)

# SET: sets a key to a value. Returns True if successful.
r.set('user:1:name', 'Alice')

# GET: retrieves the value for a key.
name = r.get('user:1:name')
print(f"Name: {name}") # Output: Name: Alice

# INCR: increments an integer value. Redis handles the string conversion.
r.set('page_views', 100)
r.incr('page_views')
views = r.get('page_views')
print(f"Page views: {views}") # Output: Page views: 101

# SET with expiration: Set a key that will automatically delete after a time.
# ex=10 means it will expire in 10 seconds.
r.set('temporary_key', 'this will disappear', ex=10)
```

### Hashes

Hashes are maps between string fields and string values. They are the perfect data type for storing objects. Instead of creating keys like `user:1:name`, `user:1:email`, you can have a single `user:1` hash with fields `name` and `email`.

```python
# hashes_example.py
import redis

r = redis.Redis(decode_responses=True)
user_id = 'user:1001'

# HSET: sets fields in a hash. Can set multiple at once with `mapping`.
r.hset(user_id, mapping={
    'name': 'Bob',
    'email': 'bob@example.com',
    'country': 'USA'
})

# HGET: gets the value of a single field.
user_name = r.hget(user_id, 'name')
print(f"User name: {user_name}") # Output: User name: Bob

# HGETALL: gets all fields and values in the hash as a Python dictionary.
user_data = r.hgetall(user_id)
print(f"All user data: {user_data}")
# Output: All user data: {'name': 'Bob', 'email': 'bob@example.com', 'country': 'USA'}
```

### Lists

A list of strings, sorted by insertion order. You can push items to the left (head) or right (tail).

```python
# lists_example.py
import redis

r = redis.Redis(decode_responses=True)
queue_name = 'job_queue'

# Clear the list for a clean run
r.delete(queue_name)

# RPUSH: push items to the right (end) of the list.
r.rpush(queue_name, 'job1', 'job2', 'job3')

# LPUSH: push an item to the left (start) of the list.
r.lpush(queue_name, 'urgent_job')

# LRANGE: get a range of items from the list. (0, -1) means all items.
all_jobs = r.lrange(queue_name, 0, -1)
print(f"Current jobs in queue: {all_jobs}")
# Output: Current jobs in queue: ['urgent_job', 'job1', 'job2', 'job3']

# LPOP: remove and return the first item from the left (head).
next_job = r.lpop(queue_name)
print(f"Processing job: {next_job}") # Output: Processing job: urgent_job

remaining_jobs = r.lrange(queue_name, 0, -1)
print(f"Remaining jobs: {remaining_jobs}") # Output: Remaining jobs: ['job1', 'job2', 'job3']
```

### Sets

An unordered collection of unique strings. You can add, remove, and test for existence in O(1) time (very fast).

```python
# sets_example.py
import redis

r = redis.Redis(decode_responses=True)
attendees_key = 'event:tech_conference:attendees'

r.delete(attendees_key)

# SADD: add members to a set. Duplicates are ignored.
r.sadd(attendees_key, 'Alice', 'Bob', 'Charlie')
r.sadd(attendees_key, 'Alice') # This does nothing, as Alice is already a member.

# SMEMBERS: get all members of the set.
all_attendees = r.smembers(attendees_key)
print(f"All attendees: {all_attendees}") # Order is not guaranteed

# SISMEMBER: check if a value is a member of the set.
is_attending = r.sismember(attendees_key, 'Bob')
print(f"Is Bob attending? {is_attending}") # Output: Is Bob attending? True

# SREM: remove a member.
r.srem(attendees_key, 'Charlie')
print(f"Attendees after Charlie left: {r.smembers(attendees_key)}")
```

### Sorted Sets (ZSETs)

Similar to Sets, but every member has an associated floating-point `score`. Members are unique, and the collection is ordered by the score. This is ideal for leaderboards.

```python
# sorted_sets_example.py
import redis

r = redis.Redis(decode_responses=True)
leaderboard_key = 'game:leaderboard'

r.delete(leaderboard_key)

# ZADD: add members with scores. Can be done with a mapping.
r.zadd(leaderboard_key, {
    'player_one': 1500,
    'player_two': 2300,
    'player_three': 950
})

# Add another player
r.zadd(leaderboard_key, {'player_four': 2100})

# ZREVRANGE: get a range of members, ordered from highest score to lowest.
# withscores=True also returns the scores.
top_3 = r.zrevrange(leaderboard_key, 0, 2, withscores=True)
print(f"Top 3 Players: {top_3}")
# Output: Top 3 Players: [('player_two', 2300.0), ('player_four', 2100.0), ('player_one', 1500.0)]

# ZRANK: get the rank of a member (0-based, lowest score is rank 0).
rank = r.zrank(leaderboard_key, 'player_one')
print(f"Player One's rank (low to high): {rank}") # Output: Player One's rank (low to high): 1

# ZSCORE: get the score of a specific member.
score = r.zscore(leaderboard_key, 'player_two')
print(f"Player Two's score: {score}") # Output: Player Two's score: 2300.0
```

## 5. Summary

*   Redis is a fast, in-memory, key-value store with powerful data structures.
*   It excels at caching, session management, real-time analytics, and more.
*   The `redis-py` library is the standard way to interact with Redis in Python.
*   Understanding the core data types (Strings, Hashes, Lists, Sets, Sorted Sets) is key to using Redis effectively. Choose the right data type for your problem!

