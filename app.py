from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
from flask_cors import CORS
import secrets
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database connection parameters
db_params = {
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT")
}

def connect_to_database():
    return psycopg2.connect(**db_params)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'message': 'This is JSON data from your Flask API!',
        'status': 'success'
    }
    return jsonify(data)

# @app.route('/api/login', methods=['POST'])
# def login():
#     # Get user input from the request
#     data = request.get_json()
#     work_email = data.get('work_email')
#     password = data.get('password')

#     # Check user credentials in the database
#     try:
#         conn = connect_to_database()
#         cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#         cursor.execute("SELECT * FROM users WHERE work_email = %s AND password = %s", (work_email, password))
#         user = cursor.fetchone()

#         if user:
#             return jsonify({'message': 'Login successful', 'status': 'success'})
#         else:
#             return jsonify({'message': 'Invalid username or password', 'status': 'error'})
#     except Exception as e:
#         return jsonify({'message': 'An error occurred', 'status': 'error'})
#     finally:
#         cursor.close()
#         conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE user_id = %s", (user_id,))
    db_password = cursor.fetchone()
    cursor.close()

    if db_password and db_password[0] == password:
        user = User(user_id)
        login_user(user)
        return {'message': 'Login successful'}
    else:
        return {'message': 'Login failed'}, 401
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return {'message': 'Logout successful'}

@app.route('/protected')
@login_required
def protected():
    # You can put any protected API logic here
    return {'message': 'You are logged in and active.'}



if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)