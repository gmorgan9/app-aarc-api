from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_cors import CORS
import secrets
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt, check_password_hash

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# Define the User model
class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    work_email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def get_id(self):
        return str(self.user_id)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'https://app-aarc.morganserver.com/'  # Replace with your login route
login_manager.init_app(app)

# Define the user_loader function
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(int(user_id))

# Your '/dashboard' route
@app.route('/dashboard')
@login_required
def dashboard():
    # Your dashboard logic here
    return redirect('https://app-aarc.morganserver.com/dashboard')


# login
@app.route('/api/login', methods=['POST'])
def login():
    work_email = request.form.get('work_email')
    password = request.form.get('password')

    user = Users.query.filter_by(work_email=work_email).first()
    if user and check_password_hash(user.password, password):
        # Password matches; you can proceed with login
        login_user(user)  # Log the user in
        return redirect(url_for('dashboard'))  # Redirect to the dashboard
    else:
        # Password doesn't match or user doesn't exist
        return jsonify({'message': 'Login failed'}), 401
    

# Add this route to your Flask app
@app.route('/api/user')
@login_required
def get_user_info():
    # Access the current user and return their information
    user_info = {
        "work_email": current_user.work_email,
        # Add other user attributes here if needed
    }
    return jsonify(user_info)



# Your '/api/logout' route
@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)
