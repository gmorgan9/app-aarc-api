from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_cors import CORS
from flask_bcrypt import Bcrypt

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")  # Load SQLAlchemy URI from .env
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    work_email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    work_email = data.get('work_email')
    password = data.get('password')

    # Check if the user exists
    user = User.query.filter_by(work_email=work_email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        # Authentication successful
        return jsonify({"message": "Login successful"}), 200
    else:
        # Authentication failed
        return jsonify({"message": "Login failed"}), 401

if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)
