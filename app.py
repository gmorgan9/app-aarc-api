from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret'  # Change this to a strong, random secret key
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# For demonstration purposes, let's have a dictionary to store user data.
users = {
    'user1': {'username': 'user1', 'password': bcrypt.generate_password_hash('password1').decode('utf-8'), 'name': 'User One'},
    'user2': {'username': 'user2', 'password': bcrypt.generate_password_hash('password2').decode('utf-8'), 'name': 'User Two'}
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users.get(username)

    if user and bcrypt.check_password_hash(user['password'], password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)

    return jsonify({'message': 'Login failed'}), 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Logout is handled by simply not using the JWT token anymore on the client-side.
    return jsonify({'message': 'Logged out'})

@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    user = users.get(current_user)
    
    if user:
        return jsonify({'username': user['username'], 'name': user['name']})
    
    return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=False, host='100.118.102.62', port=5000)
