from flask import Flask, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_cors import CORS
import secrets
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from functools import wraps

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")  # Use your actual database URL
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'https://app-aarc.morganserver.com/'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

protected_urls = ['https://app-aarc.morganserver.com/dashboard/']

def login_required_for_protected(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to be logged in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return func(*args, **kwargs)
    return decorated_view

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

    user = User.query.filter_by(work_email=work_email).first()

    if user and user.password == password:
        login_user(user)
        return redirect('https://app-aarc.morganserver.com/dashboard/')
    else:
        return jsonify({'message': 'Invalid username or password', 'status': 'error'})

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
