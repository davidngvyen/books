import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    #flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    #database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'bookstore')
    
    #jwt tokens
    JWT_SECRET = os.getenv('JWT_SECRET', SECRET_KEY)
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
