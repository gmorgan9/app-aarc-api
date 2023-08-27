from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_cors import CORS
import secrets
from flask_bcrypt import Bcrypt
import jwt
from functools import wraps
from datetime import datetime, timedelta

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)  # Generate a new secret key each time the application runs (not recommended for production)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")  # Load SQLAlchemy URI from .env
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")

# Define your User model
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    work_email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Decorator to ensure the request has a valid token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# User login
@app.route('/api/login', methods=['POST'])
def login():
    work_email = request.json.get('work_email')
    password = request.json.get('password')

    user = User.query.filter_by(work_email=work_email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        token = jwt.encode({'user_id': user.user_id, 'exp': datetime.utcnow() + timedelta(hours=1)},
                           app.secret_key, algorithm='HS256')
        return jsonify({'token': token.decode('utf-8')}), 200
    else:
        return jsonify({'message': 'Login failed'}), 401

# Protected route
@app.route('/api/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({'message': 'This is a protected route'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
