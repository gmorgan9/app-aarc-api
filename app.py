from flask import Flask, jsonify, request, redirect, url_for, flash, render_template
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
from flask_cors import CORS
import secrets
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
import bcrypt  # Add bcrypt for password hashing

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Change to the login route

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
    with connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT work_email FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return User(user_data[0])
        else:
            return None

def hash_password(password):
    # Hash the password using bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(password, hashed_password):
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'message': 'This is JSON data from your Flask API!',
        'status': 'success'
    }
    return jsonify(data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        work_email = request.form['work_email']
        password = request.form['password']

        try:
            with connect_to_database() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, password FROM users WHERE work_email = %s", (work_email,))
                user_data = cursor.fetchone()
                
                if user_data and check_password(password, user_data[1]):
                    user = User(user_data[0])
                    login_user(user)

                    # Redirect to the dashboard upon successful login
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'error')
        except Exception as e:
            flash('An error occurred', 'error')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Protected dashboard route
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)