from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_cors import CORS
import secrets
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt, check_password_hash  # Import Bcrypt

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")  # Use your actual database URL
db = SQLAlchemy(app)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# Define the User model
class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    work_email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'https://app-aarc.morganserver.com/'  # Replace with your login route
login_manager.init_app(app)

# Login route
@app.route('/api/login', methods=['POST'])
def login():
    work_email = request.json.get('work_email')
    password = request.json.get('password')

    user = Users.query.filter_by(work_email=work_email).first()
    if user and check_password_hash(user.password, password):
        # Password matches; you can proceed with login
        return jsonify({'message': 'Login successful'})
    else:
        # Password doesn't match or user doesn't exist
        return jsonify({'message': 'Login failed'}), 401

# Logout route
@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)
