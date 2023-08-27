from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_cors import CORS
from flask_bcrypt import Bcrypt

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")  # Load SQLAlchemy URI from .env
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    work_email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    logged_in = db.Column(db.Integer, default=0)  # Set logged_in as an integer



@app.route('/api/login', methods=['POST'])
def login():
    work_email = request.form.get('work_email')
    password = request.form.get('password')

    # Check if the user exists
    user = User.query.filter_by(work_email=work_email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        # Authentication successful
        user.logged_in = 1  # Set the logged_in status to 1
        db.session.commit()  # Commit the changes to the database

        # Set session items
        session['user_id'] = user.user_id  # You can store any user-related data in the session

        return jsonify({"message": "Login successful"}), 200
    else:
        # Authentication failed
        return jsonify({"message": "Login failed"}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    # Assuming you have some form of user authentication, get the current user
    # You may use session management, JWT, or some other method to identify the user
    # For demonstration purposes, let's assume you get the user's ID from the request
    user_id = request.form.get('user_id')

    # Find the user by ID
    user = User.query.get(user_id)

    if user:
        user.logged_in = 0  # Set the logged_in status to 0 to indicate logout
        db.session.commit()  # Commit the changes to the database
        return jsonify({"message": "Logout successful"}), 200
    else:
        return jsonify({"message": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)
