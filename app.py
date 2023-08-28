import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_session import Session

# Define your SQL query to check login credentials
CHECK_LOGIN = """SELECT user_id, work_email, password FROM users WHERE work_email = %s;"""

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session security
bcrypt = Bcrypt(app)

url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)
login_manager = LoginManager(app)
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem to store sessions
Session(app)

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, work_email):
        self.id = user_id
        self.work_email = work_email

# Configure Flask-Login to load users
@login_manager.user_loader
def load_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, work_email FROM users WHERE user_id = %s;", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data[0], user_data[1])

@app.route('/api/login', methods=['POST'])
def login():
    # Get login credentials from the request data
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Check the credentials (you should validate against your database)
    if username == 'your_username' and bcrypt.check_password_hash('your_hashed_password', password):
        session['username'] = username  # Store the username in the session
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return jsonify({"message": "Logged out"})

@app.route('/api/profile')
def profile():
    # Check if a user is logged in
    if 'username' in session:
        username = session['username']
        return f"Welcome, {username}! This is your profile."
    else:
        return "You are not logged in."

@app.route('/api/check_login')
def check_login():
    # Check if a user is logged in
    if 'username' in session:
        return jsonify({"loggedIn": True})
    else:
        return jsonify({"loggedIn": False})



if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True, host='100.118.102.62', port=5000)
