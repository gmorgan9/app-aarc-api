from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta
from functools import wraps
import secrets

app = Flask(__name__)

# Generate a secure secret key
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

# Dummy user data for demonstration purposes
users = {
    'user1': 'password1',
    'user2': 'password2'
}

# Helper function to generate JWT tokens
def generate_token(username):
    expiration_time = datetime.utcnow() + timedelta(hours=1)  # Token expiration time
    payload = {'username': username, 'exp': expiration_time}
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Decorator function to protect routes that require authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# Route to handle user login and token generation
@app.route('/api/auth/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify'}), 401

    if users.get(auth.username) == auth.password:
        token = generate_token(auth.username)
        return jsonify({'token': token})

    return jsonify({'message': 'Could not verify'}), 401

# Protected route to display user details
@app.route('/api/user', methods=['GET'])
@token_required
def get_user(current_user):
    return jsonify({'user': current_user})

if __name__ == '__main__':
    app.run(debug=False, host='100.118.102.62', port=5000)
