from queue import Queue
from threading import Lock
import pymysql
from pymysql.cursors import DictCursor
from config import Config

class PyMySQLConnectionPool:
    def __init__(self, size=5):
        self._size = size
        self._pool = Queue(maxsize=size)
        self._lock = Lock()
        self._initialize_pool()

    def _create_connection(self):
        return pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            autocommit=False,
            cursorclass=DictCursor
        )

    def _initialize_pool(self):
        for _ in range(self._size):
            self._pool.put(self._create_connection())

    def get_connection(self):
        conn = self._pool.get()
        try:
            conn.ping(reconnect=True)
            return conn
        except Exception:
            with self._lock:
                return self._create_connection()

    def release_connection(self, conn):
        if conn is None:
            return
        if not conn.open:
            conn = self._create_connection()
        self._pool.put(conn)

db_pool = PyMySQLConnectionPool(size=Config.DB_POOL_SIZE)

def get_db_connection():
    return db_pool.get_connection()

def release_db_connection(conn):
    db_pool.release_connection(conn)

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    #runs a query and returns results
    conn = get_db_connection()
    cursor = conn.cursor()
    result = None
    
    try:
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        
        if commit:
            conn.commit()
            result = cursor.lastrowid if cursor.lastrowid else cursor.rowcount
            
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        release_db_connection(conn)
    
    return result
