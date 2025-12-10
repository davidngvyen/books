import mysql.connector
from mysql.connector import pooling
from config import Config

#connection pool
db_pool = pooling.MySQLConnectionPool(
    pool_name="bookstore_pool",
    pool_size=10,
    pool_reset_session=True,
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME,
    autocommit=False
)

def get_db_connection():
    return db_pool.get_connection()

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    #runs a query and returns results
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
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
        conn.close()
    
    return result
