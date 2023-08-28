import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

# Define your SQL query to check login credentials
CHECK_LOGIN = """SELECT user_id, username, password FROM users WHERE username = %s;"""

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

# Configure Flask-Login to load users
@login_manager.user_loader
def load_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, username FROM users WHERE user_id = %s;", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data[0], user_data[1])

@app.post("/api/login")
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CHECK_LOGIN, (username,))
            user_data = cursor.fetchone()

    if user_data and bcrypt.check_password_hash(user_data[2], password):
        user = User(user_data[0], username)
        login_user(user)  # Log the user in
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/logout")
@login_required  # Requires authentication
def logout():
    logout_user()  # Log the user out
    return jsonify({"message": "Logged out"})

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True, host='100.118.102.62', port=5000)
