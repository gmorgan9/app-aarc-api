from flask import Flask, jsonify, request, redirect
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
login_manager.login_view = 'https://app-aarc.morganserver.com/'

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

@login_manager.user_loader
def load_user(user_id):
    # Load a user from your database by their user_id
    # Replace this with your database logic
    user = User.query.get(int(user_id))
    return user

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'message': 'This is JSON data from your Flask API!',
        'status': 'success'
    }
    return jsonify(data)



@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    work_email = data.get('work_email')
    password = data.get('password')

    try:
        with connect_to_database() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE work_email = %s", (work_email,))
            db_password = cursor.fetchone()
            
            if db_password and db_password[0] == password:
                user = User(work_email)
                login_user(user)
                return jsonify({'message': 'Login successful', 'status': 'success'})
            else:
                return jsonify({'message': 'Invalid username or password', 'status': 'error'})
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'status': 'error'})




@app.route('/api/check_login', methods=['GET'])
@login_required
def check_login():
    return jsonify({'message': 'You are logged in', 'status': 'success'})

    
@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return redirect('https://app-aarc.morganserver.com/')

@app.route('/protected')
@login_required
def protected():
    # You can put any protected API logic here
    return {'message': 'You are logged in and active.'}



if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)