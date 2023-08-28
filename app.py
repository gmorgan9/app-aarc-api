from flask import Flask, request, jsonify, session, g

app = Flask(__name__)

# Set a secret key for session management (change this to something random)
app.secret_key = 'your_secret_key'

# For demonstration purposes, let's have a dictionary to store user data.
users = {
    'user1': {'username': 'user1', 'password': 'password1', 'name': 'User One'},
    'user2': {'username': 'user2', 'password': 'password2', 'name': 'User Two'}
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check if the username and password match
    user = users.get(username)
    if user and user['password'] == password:
        session['user'] = user
        return jsonify({'message': 'Login successful'})

    return jsonify({'message': 'Login failed'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out'})

@app.route('/user')
def get_user():
    if 'user' in session:
        user = session['user']
        return jsonify({'username': user['username'], 'name': user['name']})

    return jsonify({'message': 'Not logged in'}), 401

if __name__ == '__main__':
    app.run(debug=False, host='100.118.102.62', port=5000)