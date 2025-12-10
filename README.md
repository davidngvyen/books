'backend/' – Flask API
'desktop_client/' – Python desktop app (Tkinter GUI)

Run the backend first, then run the desktop client.

1. What you need installed
PythonMySQL Server
'pip'

Python packages you will probably need:
Backend
powershell
pip install flask flask-cors python-dotenv pymysql bcrypt pyjwt

Desktop client
powershell
pip install requests

2. Set up the database

1. Start MySQL on your computer.
2. Create a database called 'bookstore'.
3. Run the SQL file in 'database/schema.sql' to create tables.


3. Create a '.env' file
Example '.env':

env
#Flask secret key
SECRET_KEY=dev-secret-key-change-this


#Database connection
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=bookstore

#JWT secret for tokens
JWT_SECRET=another-secret-key-here

#CORS allowed origins
CORS_ORIGINS=*

Change 'DB_USER' and 'DB_PASSWORD' to match your local MySQL user.

4. Run the backend
In a terminal: python app.py
Keep this terminal open.

5. Run the desktop client
Open a new terminal run: python main.py

A window should open for the bookstore app.
