from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from flask_wtf.csrf import CSRFProtect
import secrets

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")  # Load SQLAlchemy URI from .env
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Generate a secure secret key
secret_key = secrets.token_hex(16)  # Change the length as needed

# Set the Flask app's secret key
app.secret_key = secret_key

csrf = CSRFProtect(app)  # Initialize CSRF protection after setting secret key

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    work_email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __init__(self, work_email, password):
        self.work_email = work_email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')



@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    # Check if the request contains a username and password
    if 'work_email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing work_email or password'}), 400

    # Try to find a user with the provided username
    user = User.query.filter_by(work_email=data['work_email']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        # Password is correct, generate a token or session here if needed
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401




if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)
