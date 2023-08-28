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
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)
bcrypt = Bcrypt(app)
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

@app.post("/api/login")
def login():
    data = request.get_json()
    work_email = data.get("work_email")
    password = data.get("password")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CHECK_LOGIN, (work_email,))
            user_data = cursor.fetchone()

    if user_data and bcrypt.check_password_hash(user_data[2], password):
        user = User(user_data[0], work_email)
        login_user(user)  # Log the user in
        session['user_id'] = user.id  # Store user's ID in the session
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/logout")
@login_required  # Requires authentication
def logout():
    logout_user()  # Log the user out
    session.pop('user_id', None)  # Remove user's ID from the session
    return jsonify({"message": "Logged out"})

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True, host='100.118.102.62', port=5000)
