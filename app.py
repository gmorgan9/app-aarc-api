from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key
api = Api(app)
jwt = JWTManager(app)


users = {
    'user1': {'password': 'password1', 'email': 'user1@example.com'},
    'user2': {'password': 'password2', 'email': 'user2@example.com'}
}


class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if username in users and users[username]['password'] == password:
            access_token = create_access_token(identity=username)
            return {'access_token': access_token}, 200
        return {'message': 'Invalid credentials'}, 401

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        # JWT revocation logic (if needed)
        return {'message': 'Successfully logged out'}, 200

api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')


class UserProfile(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        if current_user in users:
            user_data = users[current_user]
            return user_data, 200
        return {'message': 'User not found'}, 404

api.add_resource(UserProfile, '/profile')


if __name__ == '__main__':
    app.run(debug=False, host='100.118.102.62', port=5000)
